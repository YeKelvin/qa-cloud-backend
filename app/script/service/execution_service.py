#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_service.py
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
import traceback

import flask
from pymeter.runner import Runner

from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.exceptions import ServiceError
from app.common.id_generator import new_id
from app.common.validator import check_is_not_blank
from app.extension import db
from app.extension import executor
from app.extension import socketio
from app.script.dao import element_children_dao as ElementChildrenDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.dao import test_report_dao as TestReportDao
from app.script.dao import testplan_dao as TestPlanDao
from app.script.dao import testplan_execution_dao as TestplanExecutionDao
from app.script.dao import testplan_execution_items_dao as TestPlanExecutionItemsDao
from app.script.dao import testplan_items_dao as TestPlanItemsDao
from app.script.dao import testplan_settings_dao as TestPlanSettingsDao
from app.script.dao import variable_dataset_dao as VariableDatasetDao
from app.script.enum import ElementType
from app.script.enum import RunningState
from app.script.enum import VariableDatasetType
from app.script.enum import is_test_snippets
from app.script.model import TTestplanExecution
from app.script.model import TTestplanExecutionDataset
from app.script.model import TTestplanExecutionItems
from app.script.model import TTestplanExecutionSettings
from app.script.model import TTestReport
from app.script.service import element_loader
from app.utils.log_util import get_logger
from app.utils.time_util import timestamp_now
from app.utils.time_util import timestamp_to_utc8_datetime


log = get_logger(__name__)


def debug_pymeter(script, sid):
    # noinspection PyBroadException
    try:
        Runner.start([script], throw_ex=True, use_sio_log_handler=True, ext={'sio': socketio, 'sid': sid})
        socketio.emit('pymeter_completed', namespace='/', to=sid)
    except Exception:
        log.error(traceback.format_exc())
        socketio.emit('pymeter_error', '脚本执行异常', namespace='/', to=sid)


@http_service
def execute_collection(req):
    # 查询元素
    collection = TestElementDao.select_by_no(req.collectionNo)
    if not collection.ENABLED:
        raise ServiceError('元素已禁用')
    if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
        raise ServiceError('仅支持运行 Collecion 元素')

    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_tree(req.collectionNo)
    if not script:
        raise ServiceError('脚本异常，请检查后重试')

    # 添加 socket 组件
    element_loader.add_flask_sio_result_collector(script, req.socketId, collection.ELEMENT_NAME)

    # 添加变量组件
    if req.variableDataSet:
        element_loader.add_variable_data_set(
            script, req.variableDataSet.numberList, req.variableDataSet.useCurrentValue
        )

    # TODO: 暂时用ThreadPoolExecutor，后面改用Celery，https://www.celerycn.io/
    # 新建线程执行脚本
    executor.submit(debug_pymeter, script, req.socketId)


@http_service
def execute_group(req):
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
    collection_no = group_parent_link.PARENT_NO

    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_tree(collection_no, specified_group_no=req.groupNo, specified_self_only=req.selfOnly)
    if not script:
        raise ServiceError('脚本异常，请检查后重试')

    # 添加 socket 组件
    element_loader.add_flask_sio_result_collector(script, req.socketId, group.ELEMENT_NAME)

    # 添加变量组件
    if req.variableDataSet:
        element_loader.add_variable_data_set(
            script, req.variableDataSet.numberList, req.variableDataSet.useCurrentValue
        )

    # 新建线程执行脚本
    executor.submit(debug_pymeter, script, req.socketId)


@http_service
def execute_sampler(req):
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
    collection_no = sampler_parent_link.ROOT_NO
    group_no = sampler_parent_link.PARENT_NO

    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_tree(collection_no, group_no, req.samplerNo, req.selfOnly)
    if not script:
        raise ServiceError('脚本异常，请检查后重试')

    # 添加 socket 组件
    element_loader.add_flask_sio_result_collector(script, req.socketId, sampler.ELEMENT_NAME)

    # 添加变量组件
    if req.variableDataSet:
        element_loader.add_variable_data_set(
            script, req.variableDataSet.numberList, req.variableDataSet.useCurrentValue
        )

    # 新建线程执行脚本
    executor.submit(debug_pymeter, script, req.socketId)


@http_service
def execute_snippet_collection(req):
    # 查询元素
    collection = TestElementDao.select_by_no(req.collectionNo)
    if not collection.ENABLED:
        raise ServiceError('元素已禁用')
    if not is_test_snippets(collection):
        raise ServiceError('仅支持运行 TestSnippets 元素')

    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_snippet_collecion(
        collection.ELEMENT_NO, collection.ELEMENT_NAME, collection.ELEMENT_REMARK
    )
    if not script:
        raise ServiceError('脚本异常，请检查后重试')

    # 添加 socket 组件
    element_loader.add_flask_sio_result_collector(script, req.socketId, collection.ELEMENT_NAME)

    # 添加变量组件
    if req.variableDataSet:
        element_loader.add_variable_data_set(
            script, req.variableDataSet.numberList, req.variableDataSet.useCurrentValue, req.variables
        )

    # 新建线程执行脚本
    executor.submit(debug_pymeter, script, req.socketId)


@http_service
@transactional
def execute_testplan(req):
    # 查询是否有正在运行中的执行任务
    running = TestplanExecutionDao.select_running_by_plan(req.planNo)
    if running:
        raise ServiceError('测试计划正在运行中，请执行结束后再开始新的执行')

    # 查询测试计划
    testplan = TestPlanDao.select_by_no(req.planNo)
    check_is_not_blank(testplan, '测试计划不存在')

    # 查询测试计划设置项
    settings = TestPlanSettingsDao.select_by_no(req.planNo)
    check_is_not_blank(settings, '计划设置不存在')

    # 查询测试计划关联的集合
    items = TestPlanItemsDao.select_all_by_plan(req.planNo)
    if not items:
        raise ServiceError('测试计划中无关联的脚本')
    # 根据序号排序
    items.sort(key=lambda k: k.SORT_NO)
    collection_number_list = [item.COLLECTION_NO for item in items]

    # 创建执行编号
    execution_no = new_id()
    # 创建执行记录与数据集关联
    environment = None
    for dataset_no in req.datasetNumberList:
        dataset = VariableDatasetDao.select_by_no(dataset_no)
        if dataset.DATASET_TYPE == VariableDatasetType.ENVIRONMENT.value:
            environment = dataset.DATASET_NAME
        TTestplanExecutionDataset.insert(
            EXECUTION_NO=execution_no,
            DATASET_NO=dataset_no
        )
    # 创建执行记录
    TTestplanExecution.insert(
        PLAN_NO=req.planNo,
        EXECUTION_NO=execution_no,
        RUNNING_STATE=RunningState.WAITING.value,
        ENVIRONMENT=environment,
        TEST_PHASE=testplan.TEST_PHASE
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
        USE_CURRENT_VALUE=req.useCurrentValue
    )
    # 创建计划执行项目明细
    for item in items:
        TTestplanExecutionItems.insert(
            EXECUTION_NO=execution_no,
            COLLECTION_NO=item.COLLECTION_NO,
            SORT_NO=item.SORT_NO,
            RUNNING_STATE=RunningState.WAITING.value
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
            REPORT_NAME=testplan.PLAN_NAME
        )

    # 异步函数
    def start(app):
        # noinspection PyBroadException
        try:
            with app.app_context():
                run_testplan(
                    app,
                    collection_number_list, req.datasetNumberList, req.useCurrentValue, execution_no, report_no
                )
        except Exception:
            log.error(f'执行编号:[ {execution_no} ] 发生异常\n{traceback.format_exc()}')
            with app.app_context():
                # noinspection PyBroadException
                try:
                    TestPlanDao.update_running_state_by_no(execution_no, RunningState.ERROR.value)
                except Exception:
                    log.error(f'执行编号:[ {execution_no} ] 发生异常\n{traceback.format_exc()}')

    # 先提交事务，防止新线程查询计划时拿不到
    db.session.commit()
    # 异步执行脚本
    executor.submit(start, flask.current_app._get_current_object())

    return {'executionNo': execution_no, 'total': len(items)}


def run_testplan(app, collection_number_list, dataset_number_list, use_current_value, execution_no, report_no=None):
    log.info(f'执行编号:[ {execution_no} ] 开始执行测试计划')
    # 记录开始时间
    start_time = timestamp_now()
    # 查询执行记录
    execution = TestplanExecutionDao.select_by_no(execution_no)
    # 更新运行状态
    execution.update(RUNNING_STATE=RunningState.RUNNING.value)
    db.session.commit()  # 这里要实时更新

    # 顺序执行脚本
    for collection_no in collection_number_list:
        # 查询计划项目
        item = TestPlanExecutionItemsDao.select_by_execution_and_collection(execution_no, collection_no)
        # 更新项目运行状态
        item.update(RUNNING_STATE=RunningState.RUNNING.value)
        db.session.commit()  # 这里要实时更新
        # 加载脚本
        collection = element_loader.loads_tree(collection_no, no_debuger=True)
        if not collection:
            log.warning(f'执行编号:[ {execution_no} ] 集合编号:[ {collection_no} ] 脚本为空或脚本已禁用，跳过当前脚本')

        # 添加自定义变量组件
        if dataset_number_list:
            element_loader.add_variable_data_set(collection, dataset_number_list, use_current_value)

        # 添加报告存储器组件
        if report_no:
            element_loader.add_flask_db_result_storage(collection, execution_no, report_no, collection_no)

        # 异步函数
        def start(app):
            # noinspection PyBroadException
            try:
                log.info(f'执行编号:[ {execution_no} ] 集合名称:[ {collection["name"]} ] 开始执行脚本')
                Runner.start([collection], throw_ex=True)
            except Exception:
                log.error(f'执行编号:[ {execution_no} ] 集合编号:[ {collection_no} ] 脚本执行异常\n{traceback.format_exc()}')
                with app.app_context():
                    # noinspection PyBroadException
                    try:
                        item.update(RUNNING_STATE=RunningState.ERROR.value)
                    except Exception:
                        log.error(f'执行编号:[ {execution_no} ] 集合编号:[ {collection_no} ] 发生异常\n{traceback.format_exc()}')

        task = executor.submit(start, app)  # 异步执行脚本
        task.result()  # 阻塞等待脚本执行完成
        # 更新项目运行状态
        item.update(RUNNING_STATE=RunningState.COMPLETED.value)
        db.session.commit()  # 这里要实时更新
        log.info(f'执行编号:[ {execution_no} ] 集合名称:[ {collection["name"]} ] 脚本执行完成')

    if report_no:
        # 记录结束时间
        end_time = timestamp_now()
        # 计算耗时
        elapsed_time = int(end_time * 1000) - int(start_time * 1000)
        # 更新报告的开始时间、结束时间和耗时
        TestReportDao.select_by_no(report_no).update(
            START_TIME=timestamp_to_utc8_datetime(start_time),
            END_TIME=timestamp_to_utc8_datetime(end_time),
            ELAPSED_TIME=elapsed_time
        )

    # 更新运行状态
    execution.update(RUNNING_STATE=RunningState.COMPLETED.value)
    db.session.commit()  # 这里要实时更新
    log.info(f'执行编号:[ {execution_no} ] 测试计划执行完成')
