#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_service.py
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
import time
import traceback

import flask
from pymeter.runner import Runner

from app import config as CONFIG
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.exceptions import ServiceError
from app.common.globals import get_userno
from app.common.identity import new_id
from app.common.validator import check_exists
from app.common.validator import check_workspace_permission
from app.extension import db
from app.extension import executor
from app.extension import socketio
from app.public.dao import notification_robot_dao as NotificationRobotDao
from app.public.enum import RobotState
from app.public.enum import RobotType
from app.script.dao import element_children_dao as ElementChildrenDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.dao import test_group_result_dao as TestGroupResultDao
from app.script.dao import test_report_dao as TestReportDao
from app.script.dao import testplan_dao as TestPlanDao
from app.script.dao import testplan_execution_dao as TestplanExecutionDao
from app.script.dao import testplan_execution_items_dao as TestPlanExecutionItemsDao
from app.script.dao import testplan_items_dao as TestPlanItemsDao
from app.script.dao import testplan_settings_dao as TestPlanSettingsDao
from app.script.dao import variable_dataset_dao as VariableDatasetDao
from app.script.dao import workspace_collection_dao as WorkspaceCollectionDao
from app.script.enum import ElementType
from app.script.enum import RunningState
from app.script.enum import VariableDatasetType
from app.script.enum import is_snippet_collection
from app.script.model import TTestplanExecution
from app.script.model import TTestplanExecutionItems
from app.script.model import TTestplanExecutionSettings
from app.script.model import TTestReport
from app.script.service import element_loader
from app.usercenter.dao import user_dao as UserDao
from app.utils.log_util import get_logger
from app.utils.notification import wecom as WeComTool
from app.utils.time_util import datetime_now_by_utc8
from app.utils.time_util import microsecond_to_h_m_s
from app.utils.time_util import timestamp_now
from app.utils.time_util import timestamp_to_utc8_datetime


log = get_logger(__name__)


def get_root_no(element_no):
    """根据元素编号获取根元素编号（集合编号）"""
    if not (link := ElementChildrenDao.select_by_child(element_no)):
        return element_no
    if not link.ROOT_NO:
        raise ServiceError(f'元素编号:[ {element_no} ] 根元素编号为空')
    return link.ROOT_NO


def get_workspace_no(collection_no) -> str:
    """获取元素空间编号"""
    workspace_collection = WorkspaceCollectionDao.select_by_collection(collection_no)
    if not workspace_collection:
        raise ServiceError('查询元素空间失败')
    return workspace_collection.WORKSPACE_NO


def debug_pymeter(script, sid):
    # noinspection PyBroadException
    try:
        Runner.start([script], throw_ex=True, use_sio_log_handler=True, ext={'sio': socketio, 'sid': sid})
        socketio.emit('pymeter_completed', namespace='/', to=sid)
    except Exception:
        log.error(traceback.format_exc())
        socketio.emit('pymeter_error', '脚本执行异常', namespace='/', to=sid)


def debug_pymeter_by_loader(loader, app, element_no, element_name, sid):
    result_id = new_id()
    # noinspection PyBroadException
    try:
        socketio.emit(
            'pymeter_start',
            {'id': result_id, 'name': '加载中', 'loading': True, 'running': True},
            namespace='/',
            to=sid
        )
        script = loader(app, element_no, element_name, sid, result_id)
        Runner.start([script], throw_ex=True, use_sio_log_handler=True, ext={'sio': socketio, 'sid': sid})
        socketio.emit('pymeter_completed', namespace='/', to=sid)
    except Exception:
        log.error(traceback.format_exc())
        socketio.emit(
            'pymeter_result_summary',
            {'resultId': result_id, 'result': {'name': 'error', 'loading': False, 'running': False}},
            namespace='/',
            to=sid
        )
        socketio.emit('pymeter_error', '脚本执行异常', namespace='/', to=sid)


def get_flask_app():
    """获取当前 flask 实例"""
    return flask.current_app._get_current_object()  # noqa


@http_service
def execute_collection(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.collectionNo)))

    # 查询元素
    collection = TestElementDao.select_by_no(req.collectionNo)
    if not collection.ENABLED:
        raise ServiceError('元素已禁用')
    if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
        raise ServiceError('仅支持运行 Collecion 元素')

    # 定义 loader 函数
    def script_loader(app, element_no, element_name, sid, result_id):
        with app.app_context():
            # 根据 collectionNo 递归加载脚本
            script = element_loader.loads_tree(element_no)
            # 添加 socket 组件
            element_loader.add_flask_sio_result_collector(
                script,
                sid,
                result_id=result_id,
                result_name=element_name
            )
            # 添加变量组件
            if req.datasetNumberedList:
                element_loader.add_variable_dataset(
                    script,
                    req.datasetNumberedList,
                    req.useCurrentValue
                )
            return script

    # 新建线程执行脚本
    executor.submit(
        debug_pymeter_by_loader,
        script_loader,
        get_flask_app(),
        req.collectionNo,
        collection.ELEMENT_NAME,
        req.socketId
    )


@http_service
def execute_group(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.groupNo)))

    # 查询元素
    group = TestElementDao.select_by_no(req.groupNo)
    if not group.ENABLED:
        raise ServiceError('元素已禁用')
    if group.ELEMENT_TYPE != ElementType.GROUP.value:
        raise ServiceError('仅支持运行 Group 元素')

    # 获取 collectionNo
    group_parent_link = ElementChildrenDao.select_by_child(req.groupNo)
    if not group_parent_link:
        raise ServiceError('元素父级关联不存在')

    # 临时存储变量
    collection_no = group_parent_link.PARENT_NO

    # 定义 loader 函数
    def script_loader(app, element_no, element_name, sid, result_id):
        with app.app_context():
            # 根据 collectionNo 递归加载脚本
            script = element_loader.loads_tree(
                element_no,
                specified_group_no=req.groupNo,
                specified_selfonly=req.selfonly
            )
            # 添加 socket 组件
            element_loader.add_flask_sio_result_collector(
                script,
                sid,
                result_id=result_id,
                result_name=element_name
            )
            # 添加变量组件
            if req.datasetNumberedList:
                element_loader.add_variable_dataset(
                    script,
                    req.datasetNumberedList,
                    req.useCurrentValue
                )
            return script

    # 新建线程执行脚本
    executor.submit(
        debug_pymeter_by_loader,
        script_loader,
        get_flask_app(),
        collection_no,
        group.ELEMENT_NAME,
        req.socketId
    )


@http_service
def execute_sampler(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.samplerNo)))

    # 查询元素
    sampler = TestElementDao.select_by_no(req.samplerNo)
    if not sampler.ENABLED:
        raise ServiceError('元素已禁用')
    if sampler.ELEMENT_TYPE != ElementType.SAMPLER.value:
        raise ServiceError('仅支持运行 Sampler 元素')

    # 获取 collectionNo 和 groupNo
    sampler_parent_link = ElementChildrenDao.select_by_child(req.samplerNo)
    if not sampler_parent_link:
        raise ServiceError('元素父级关联不存在')

    # 临时存储变量
    collection_no = sampler_parent_link.ROOT_NO
    group_no = sampler_parent_link.PARENT_NO

    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_tree(collection_no, group_no, req.samplerNo, req.selfonly)

    # 添加 socket 组件
    result_id = new_id()
    element_loader.add_flask_sio_result_collector(
        script,
        sid=req.socketId,
        result_id=result_id,
        result_name=sampler.ELEMENT_NAME
    )

    # 添加变量组件
    if req.datasetNumberedList:
        element_loader.add_variable_dataset(
            script,
            req.datasetNumberedList,
            req.useCurrentValue
        )

    # 新建线程执行脚本
    executor.submit(debug_pymeter, script, req.socketId)


@http_service
def execute_snippets(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.collectionNo)))

    # 查询元素
    collection = TestElementDao.select_by_no(req.collectionNo)
    if not collection.ENABLED:
        raise ServiceError('元素已禁用')
    if not is_snippet_collection(collection):
        raise ServiceError('仅支持运行 SnippetCollection 元素')

    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_snippet_collecion(
        collection.ELEMENT_NO,
        collection.ELEMENT_NAME,
        collection.ELEMENT_REMARK
    )

    # 添加 socket 组件
    result_id = new_id()
    element_loader.add_flask_sio_result_collector(
        script,
        sid=req.socketId,
        result_id=result_id,
        result_name=collection.ELEMENT_NAME
    )

    # 添加变量组件
    if req.datasetNumberedList:
        element_loader.add_variable_dataset(
            script,
            req.datasetNumberedList,
            req.useCurrentValue,
            req.variables
        )

    # 新建线程执行脚本
    executor.submit(debug_pymeter, script, req.socketId)


@http_service
@transactional
def execute_testplan(req):
    return run_testplan(req.planNo, req.datasetNumberedList, req.useCurrentValue)


def run_testplan(plan_no, dataset_numbered_list, use_current_value):
    # 查询测试计划
    testplan = TestPlanDao.select_by_no(plan_no)
    check_exists(testplan, '测试计划不存在')

    # 校验空间权限
    check_workspace_permission(testplan.WORKSPACE_NO)

    # 查询是否有正在运行中的执行任务
    running = TestplanExecutionDao.select_running_by_plan(plan_no)
    if running:
        raise ServiceError('测试计划正在运行中，请执行结束后再开始新的执行')

    # 查询测试计划设置项
    settings = TestPlanSettingsDao.select_by_no(plan_no)
    check_exists(settings, '计划设置不存在')

    # 查询测试计划关联的集合
    items = TestPlanItemsDao.select_all_by_plan(plan_no)
    if not items:
        raise ServiceError('测试计划中无关联的脚本')

    # 根据序号排序
    items.sort(key=lambda k: k.SORT_NO)
    collection_numbered_list = [item.COLLECTION_NO for item in items]

    # 创建执行编号
    execution_no = new_id()
    # 创建执行记录与数据集关联
    environment = None
    for dataset_no in dataset_numbered_list:
        dataset = VariableDatasetDao.select_by_no(dataset_no)
        if dataset.DATASET_TYPE == VariableDatasetType.ENVIRONMENT.value:
            environment = dataset.DATASET_NAME
    # 创建执行记录
    TTestplanExecution.insert(
        PLAN_NO=plan_no,
        EXECUTION_NO=execution_no,
        RUNNING_STATE=RunningState.WAITING.value,
        ENVIRONMENT=environment,
        TEST_PHASE=testplan.TEST_PHASE,
        record=False
    )
    # 创建计划执行设置
    TTestplanExecutionSettings.insert(
        EXECUTION_NO=execution_no,
        CONCURRENCY=settings.CONCURRENCY,
        ITERATIONS=settings.ITERATIONS,
        DELAY=settings.DELAY,
        SAVE=settings.SAVE,
        SAVE_ON_ERROR=settings.SAVE_ON_ERROR,
        STOP_TEST_ON_ERROR_COUNT=settings.STOP_TEST_ON_ERROR_COUNT,
        VARIABLE_DATASET_LIST=dataset_numbered_list,
        USE_CURRENT_VALUE=use_current_value,
        NOTIFICATION_ROBOT_LIST=settings.NOTIFICATION_ROBOT_LIST,
        record=False
    )
    # 创建计划执行项目明细
    for item in items:
        TTestplanExecutionItems.insert(
            EXECUTION_NO=execution_no,
            COLLECTION_NO=item.COLLECTION_NO,
            SORT_NO=item.SORT_NO,
            RUNNING_STATE=RunningState.WAITING.value,
            record=False
        )
    # 新增测试报告
    report_no = None
    if settings.SAVE:
        report_no = new_id()
        TTestReport.insert(
            WORKSPACE_NO=testplan.WORKSPACE_NO,
            PLAN_NO=testplan.PLAN_NO,
            EXECUTION_NO=execution_no,
            REPORT_NO=report_no,
            REPORT_NAME=testplan.PLAN_NAME,
            record=False
        )

    # 异步函数
    def start(
            app,
            dataset_numbered_list,
            use_current_value,
            iterations,
            delay,
            save,
            save_on_error,
            notification_robot_numbered_list
    ):
        try:
            with app.app_context():
                start_testplan(
                    app,
                    collection_numbered_list,
                    dataset_numbered_list,
                    use_current_value,
                    execution_no,
                    report_no,
                    iterations,
                    delay,
                    save,
                    save_on_error,
                    notification_robot_numbered_list
                )
        except Exception:
            log.error(f'执行编号:[ {execution_no} ] 执行异常\n{traceback.format_exc()}')
            with app.app_context():
                try:
                    TestplanExecutionDao.update_running_state_by_no(execution_no, RunningState.ERROR.value)
                except Exception:
                    log.error(f'执行编号:[ {execution_no} ] 执行异常\n{traceback.format_exc()}')

    # 先提交事务，防止新线程查询计划时拿不到
    db.session.commit()
    # 异步执行脚本
    executor.submit(start,
                    get_flask_app(),
                    dataset_numbered_list,
                    use_current_value,
                    settings.ITERATIONS,
                    settings.DELAY,
                    settings.SAVE,
                    settings.SAVE_ON_ERROR,
                    settings.NOTIFICATION_ROBOT_LIST)

    return {'executionNo': execution_no, 'total': len(items)}


def start_testplan(
        app,
        collection_numbered_list,
        dataset_numbered_list,
        use_current_value,
        execution_no,
        report_no,
        iterations,
        delay,
        save,
        save_on_error,
        notification_robot_numbered_list
):
    log.info(f'执行编号:[ {execution_no} ] 开始执行测试计划')
    # 记录开始时间
    start_time = timestamp_now()
    # 查询执行记录
    execution = TestplanExecutionDao.select_by_no(execution_no)
    # 更新运行状态
    execution.update(
        RUNNING_STATE=RunningState.RUNNING.value if save else RunningState.ITERATING.value,
        START_TIME=timestamp_to_utc8_datetime(start_time),
        record=False
    )
    db.session.commit()  # 这里要实时更新

    if save:
        if save_on_error:
            start_testplan_by_error_report(
                app,
                collection_numbered_list,
                dataset_numbered_list,
                use_current_value,
                execution_no,
                report_no
            )
        else:
            start_testplan_by_report(
                app,
                collection_numbered_list,
                dataset_numbered_list,
                use_current_value,
                execution_no,
                report_no
            )
    else:
        start_testplan_by_loop(
            app,
            collection_numbered_list,
            dataset_numbered_list,
            use_current_value,
            execution_no,
            iterations,
            delay
        )

    # 记录结束时间
    end_time = timestamp_now()
    # 计算耗时
    elapsed_time = int(end_time * 1000) - int(start_time * 1000)

    report = None
    if report_no:
        # 更新报告的开始时间、结束时间和耗时
        report = TestReportDao.select_by_no(report_no)
        report.update(
            START_TIME=timestamp_to_utc8_datetime(start_time),
            END_TIME=timestamp_to_utc8_datetime(end_time),
            ELAPSED_TIME=elapsed_time,
            record=False
        )
        db.session.commit()  # 这里要实时更新

    # 重新查询执行记录
    execution = TestplanExecutionDao.select_by_no(execution_no)
    # 更新运行状态，仅运行中和迭代中才更新为已完成
    if execution.RUNNING_STATE in (RunningState.RUNNING.value, RunningState.ITERATING.value):
        execution.update(
            RUNNING_STATE=RunningState.COMPLETED.value,
            END_TIME=timestamp_to_utc8_datetime(end_time),
            ELAPSED_TIME=elapsed_time,
            record=False
        )
        db.session.commit()  # 这里要实时更新

    # 结果通知
    if notification_robot_numbered_list:
        for robot_no in notification_robot_numbered_list:
            robot = NotificationRobotDao.select_by_no(robot_no)
            if robot.STATE == RobotState.DISABLE.value:
                continue
            # 企业微信通知
            if robot.ROBOT_TYPE == RobotType.WECOM.value:
                WeComTool.text_message(
                    key=robot.ROBOT_CONFIG.get('key'),
                    content=get_notification_message(execution, report)
                )

    log.info(f'执行编号:[ {execution_no} ] 计划执行完成')


def get_notification_message(execution, report):
    testplan = TestPlanDao.select_by_no(execution.PLAN_NO)
    user = UserDao.select_by_no(execution.CREATED_BY)
    if report:
        elapsed_time = microsecond_to_h_m_s(report.ELAPSED_TIME)
        success_count = TestGroupResultDao.count_by_report_and_success(report.REPORT_NO, True)
        failure_count = TestGroupResultDao.count_by_report_and_success(report.REPORT_NO, False)
        report_url = f'{CONFIG.BASE_URL}/script/report?reportNo={report.REPORT_NO}'
        return (
            f'测试计划执行完成\n'
            f'计划名称：{testplan.PLAN_NAME}\n'
            f'执行环境：{execution.ENVIRONMENT}\n'
            f'执行人：{user.USER_NAME}\n'
            f'耗时：{elapsed_time}\n'
            f'成功：{success_count}\n'
            f'失败：{failure_count}\n'
            f'测试报告：{report_url}'
        )
    else:
        elapsed_time = microsecond_to_h_m_s(execution.ELAPSED_TIME)
        success_count = TestPlanExecutionItemsDao.sum_success_count_by_execution(execution.EXECUTION_NO)
        failure_count = TestPlanExecutionItemsDao.sum_failure_count_by_execution(execution.EXECUTION_NO)
        return (
            f'# 测试计划执行完成\n'
            f'#### 计划计划：`{testplan.PLAN_NAME}`\n'
            f'#### 执行环境：`{execution.ENVIRONMENT}`\n'
            f'#### 执行人：`{user.USER_NAME}`\n'
            f'><font color="comment">**总耗时**：{elapsed_time}</font>\n'
            f'><font color="comment">**共迭代**：{execution.ITERATION_COUNT} 次</font>\n'
            f'><font color="info">**成功迭代**：{success_count} 次</font>\n'
            f'><font color="warning">**失败迭代**：{failure_count} 次</font>'
        )


class TestplanInterruptError(Exception):
    ...


def start_testplan_by_loop(
        app,
        collection_numbered_list,
        dataset_numbered_list,
        use_current_value,
        execution_no,
        iterations,
        delay
):
    """循环运行测试计划"""
    # 批量解析脚本并临时存储
    log.info(f'执行编号:[ {execution_no} ] 开始批量解析脚本')
    scripts = {}
    for collection_no in collection_numbered_list:
        # 加载脚本
        collection = element_loader.loads_tree(collection_no, no_debuger=True)
        if not collection:
            log.warning(f'执行编号:[ {execution_no} ] 集合编号:[ {collection_no} ] 脚本为空或脚本已禁用，跳过当前脚本')
            continue
        # 添加自定义变量组件
        element_loader.add_variable_dataset(collection, dataset_numbered_list, use_current_value)
        # 添加迭代记录器组件
        element_loader.add_flask_db_iteration_storage(collection, execution_no, collection_no)
        # 存储解析后的脚本，不需要每次迭代都重新解析一遍
        scripts[collection_no] = collection

    # 批量更新计划项目的运行状态至 RUNNING
    log.info(f'执行编号:[ {execution_no} ] 脚本解析完成，开始运行测试计划')
    TestPlanExecutionItemsDao.update_running_state_by_execution(execution_no, state=RunningState.ITERATING.value)
    db.session.commit()  # 这里要实时更新

    try:
        # 循环运行
        for i in range(iterations):
            log.info(f'执行编号:[ {execution_no} ] 开始第[ {i+1} ]次迭代')
            # 记录迭代次数
            execution = TestplanExecutionDao.select_by_no(execution_no)
            execution.update(
                ITERATION_COUNT=execution.ITERATION_COUNT + 1,
                record=False
            )
            db.session.commit()  # 这里要实时更新
            # 延迟迭代
            if delay and i > 0:
                log.info(f'间隔等待{delay}ms')
                time.sleep(float(delay / 1000))
            # 顺序执行脚本
            for collection_no, collection in scripts.items():
                # 检查是否需要中断执行
                execution = TestplanExecutionDao.select_by_no(execution_no)
                if execution.INTERRUPT:
                    raise TestplanInterruptError()

                # 异步函数
                def start(app):
                    try:
                        log.info(f'执行编号:[ {execution_no} ] 集合名称:[ {collection["name"]} ] 第[ {i} ]次开始执行脚本')
                        Runner.start([collection], throw_ex=True)
                    except Exception:
                        log.error(
                            f'执行编号:[ {execution_no} ] '
                            f'集合编号:[ {collection_no} ] '
                            f'脚本执行异常\n{traceback.format_exc()}'
                        )
                        with app.app_context():
                            try:
                                item = TestPlanExecutionItemsDao.select_by_execution_and_collection(
                                    execution_no,
                                    collection_no
                                )
                                item.update(
                                    ERROR_COUNT=item.ERROR_COUNT + 1,
                                    record=False
                                )
                            except Exception:
                                log.error(
                                    f'执行编号:[ {execution_no} ] '
                                    f'集合编号:[ {collection_no} ] '
                                    f'更新异常\n{traceback.format_exc()}'
                                )

                task = executor.submit(start, app)  # 异步执行脚本
                task.result()  # 阻塞等待脚本执行完成
    except TestplanInterruptError:
        log.info(f'执行编号:[ {execution_no} ] 用户中断迭代')
    except Exception:
        log.error(f'执行编号:[ {execution_no} ] 运行异常\n{traceback.format_exc()}')
        TestPlanExecutionItemsDao.update_running_state_by_execution(execution_no, state=RunningState.ERROR.value)

    # 批量更新计划项目的运行状态至 COMPLETED
    TestPlanExecutionItemsDao.update_running_state_by_execution(execution_no, state=RunningState.COMPLETED.value)
    db.session.commit()  # 这里要实时更新
    log.info(f'执行编号:[ {execution_no} ] 计划迭代完成')


def start_testplan_by_report(
        app,
        collection_numbered_list,
        dataset_numbered_list,
        use_current_value,
        execution_no,
        report_no
):
    """运行测试计划并保存测试结果"""
    try:
        # 顺序执行脚本
        for collection_no in collection_numbered_list:
            # 检查是否需要中断执行
            execution = TestplanExecutionDao.select_by_no(execution_no)
            if execution.INTERRUPT:
                raise TestplanInterruptError()
            # 查询计划项目
            item = TestPlanExecutionItemsDao.select_by_execution_and_collection(execution_no, collection_no)
            # 更新项目运行状态
            item.update(
                RUNNING_STATE=RunningState.RUNNING.value,
                record=False
            )
            db.session.commit()  # 这里要实时更新
            # 加载脚本
            collection = element_loader.loads_tree(collection_no, no_debuger=True)
            if not collection:
                log.warning(f'执行编号:[ {execution_no} ] 集合编号:[ {collection_no} ] 脚本为空或脚本已禁用，跳过当前脚本')
            # 添加自定义变量组件
            element_loader.add_variable_dataset(collection, dataset_numbered_list, use_current_value)
            # 添加报告存储器组件
            element_loader.add_flask_db_result_storage(collection, report_no, collection_no)

            # 异步函数
            def start(app):
                try:
                    log.info(f'执行编号:[ {execution_no} ] 集合名称:[ {collection["name"]} ] 开始执行脚本')
                    Runner.start([collection], throw_ex=True)
                except Exception:
                    log.error(
                        f'执行编号:[ {execution_no} ] '
                        f'集合编号:[ {collection_no} ] '
                        f'脚本执行异常\n{traceback.format_exc()}'
                    )
                    with app.app_context():
                        try:
                            item = TestPlanExecutionItemsDao.select_by_execution_and_collection(
                                execution_no,
                                collection_no
                            )
                            item.update(
                                RUNNING_STATE=RunningState.ERROR.value,
                                record=False
                            )
                        except Exception:
                            log.error(
                                f'执行编号:[ {execution_no} ] '
                                f'集合编号:[ {collection_no} ] '
                                f'更新异常\n{traceback.format_exc()}'
                            )
            task = executor.submit(start, app)  # 异步执行脚本
            task.result()  # 阻塞等待脚本执行完成
            # 更新项目运行状态
            item.update(
                RUNNING_STATE=RunningState.COMPLETED.value,
                record=False
            )
            db.session.commit()  # 这里要实时更新
            log.info(f'执行编号:[ {execution_no} ] 集合名称:[ {collection["name"]} ] 脚本执行完成')
    except TestplanInterruptError:
        log.info(f'执行编号:[ {execution_no} ] 用户中断迭代')
    except Exception:
        log.error(f'执行编号:[ {execution_no} ] 运行异常\n{traceback.format_exc()}')
        TestPlanExecutionItemsDao.update_running_state_by_execution(execution_no, state=RunningState.ERROR.value)


def start_testplan_by_error_report(
        app,
        collection_numbered_list,
        dataset_numbered_list,
        use_current_value,
        execution_no,
        report_no
):
    """运行测试计划，但仅保存失败的测试结果"""
    ...


@http_service
@transactional
def interrupt_testplan_execution(req):
    # 查询执行记录
    execution = TestplanExecutionDao.select_by_no(req.executionNo)
    check_exists(execution, '执行记录不存在')

    # 查询测试计划
    testplan = TestPlanDao.select_by_no(execution.PLAN_NO)
    check_exists(testplan, '测试计划不存在')

    # 校验空间权限
    check_workspace_permission(testplan.WORKSPACE_NO)

    # 标记执行中断
    execution.update(
        INTERRUPT=True,
        INTERRUPT_BY=get_userno(),
        INTERRUPT_TIME=datetime_now_by_utc8(),
        RUNNING_STATE=RunningState.INTERRUPTED.value
    )


@http_service
def query_collection_json(req):
    # 查询元素
    collection = TestElementDao.select_by_no(req.collectionNo)
    if not collection.ENABLED:
        raise ServiceError('元素已禁用')
    if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
        raise ServiceError('仅支持 Collecion 元素')
    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_tree(req.collectionNo)
    # 添加变量组件
    element_loader.add_variable_dataset(script, req.datasetNumberedList, req.useCurrentValue)
    return script


@http_service
def query_group_json(req):
    # 查询元素
    group = TestElementDao.select_by_no(req.groupNo)
    if not group.ENABLED:
        raise ServiceError('元素已禁用')
    if group.ELEMENT_TYPE != ElementType.GROUP.value:
        raise ServiceError('仅支持 Group 元素')
    # 获取 collectionNo
    group_parent_link = ElementChildrenDao.select_by_child(req.groupNo)
    if not group_parent_link:
        raise ServiceError('元素父级关联不存在')
    collection_no = group_parent_link.PARENT_NO
    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_tree(collection_no, specified_group_no=req.groupNo)
    # 添加变量组件
    element_loader.add_variable_dataset(script, req.datasetNumberedList, req.useCurrentValue)
    return script


@http_service
def query_snippets_json(req):
    # 查询元素
    collection = TestElementDao.select_by_no(req.collectionNo)
    if not collection.ENABLED:
        raise ServiceError('元素已禁用')
    if not is_snippet_collection(collection):
        raise ServiceError('仅支持 SnippetCollection 元素')
    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_snippet_collecion(
        collection.ELEMENT_NO,
        collection.ELEMENT_NAME,
        collection.ELEMENT_REMARK
    )
    # 添加变量组件
    element_loader.add_variable_dataset(script, req.datasetNumberedList, req.useCurrentValue, req.variables)
    return script
