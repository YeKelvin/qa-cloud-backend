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
from app.public.dao import workspace_dao as WorkspaceDao
from app.script.dao import test_report_dao as TestReportDao
from app.script.dao import testplan_dao as TestPlanDao
from app.script.dao import testplan_item_dao as TestPlanItemDao
from app.script.enum import RunningState
from app.script.model import TTestPlan
from app.script.model import TTestPlanItem
from app.script.model import TTestPlanSettings
from app.script.model import TTestPlanVariableSetRel
from app.script.model import TTestReport
from app.script.service import element_loader
from app.utils.log_util import get_logger
from app.utils.time_util import timestamp_now
from app.utils.time_util import timestamp_to_utc8_datetime


log = get_logger(__name__)


@http_service
def execute_collection(req):
    # 根据 collectionNo 递归查询脚本数据并转换成 dict
    collection = element_loader.loads_tree(req.collectionNo)
    if not collection:
        raise ServiceError('脚本为空或脚本已禁用，请检查脚本后重新运行')

    # 添加 socket 组件
    if req.socketId:
        element_loader.add_flask_socketio_result_collector(collection, req.socketId)

    # 添加变量组件
    if req.variableSet:
        element_loader.add_variable_data_set(collection, req.variableSet.numberList, req.variableSet.useCurrentValue)

    # 新开一个线程执行脚本
    def start():
        sid = req.socketId
        try:
            Runner.start([collection], throw_ex=True)
        except Exception:
            log.error(traceback.format_exc())
            socketio.emit('pymeter_error', '脚本执行异常，请联系管理员', namespace='/', to=sid)

    # TODO: 暂时用ThreadPoolExecutor，后面改用Celery，https://www.celerycn.io/
    executor.submit(start)


@http_service
@transactional
def execute_testplan(req):
    # 查询工作空间
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_is_not_blank(workspace, '工作空间不存在')
    # 新增测试计划
    plan_no = new_id()
    TTestPlan.insert(
        WORKSPACE_NO=req.workspaceNo,
        VERSION_NO=req.versionNo,
        PLAN_NO=plan_no,
        PLAN_NAME=req.planName,
        PLAN_DESC=req.planDesc,
        TOTAL=len(req.collectionList),
        RUNNING_STATE=RunningState.RUNNING.value if req.executeNow else RunningState.WAITING.value
    )
    # 新增测试计划设置
    TTestPlanSettings.insert(
        PLAN_NO=plan_no,
        CONCURRENCY=req.concurrency,
        ITERATIONS=req.iterations,
        DELAY=req.delay,
        SAVE=req.save,
        SAVE_ON_ERROR=req.saveOnError,
        STOP_TEST_ON_ERROR_COUNT=req.stopTestOnErrorCount,
        USE_CURRENT_VALUE=req.useCurrentValue,
    )
    # 新增测试计划与变量集关联
    for set_no in req.variableSetNumberList:
        TTestPlanVariableSetRel.insert(
            PLAN_NO=plan_no,
            SET_NO=set_no
        )
    # 新增测试计划项目明细
    for collection in req.collectionList:
        TTestPlanItem.insert(
            PLAN_NO=plan_no,
            COLLECTION_NO=collection.elementNo,
            SERIAL_NO=collection.serialNo,
            RUNNING_STATE=RunningState.WAITING.value
        )
    # 新增测试报告
    report_no = None
    if req.save:
        report_no = new_id()
        TTestReport.insert(
            WORKSPACE_NO=req.workspaceNo,
            PLAN_NO=plan_no,
            REPORT_NO=report_no,
            REPORT_NAME=req.planName
        )
    # 立即执行
    if req.executeNow:
        # 异步函数
        def start(app, collection_list, set_no_list, use_current_value):
            try:
                with app.app_context():
                    run_testplan(app, collection_list, set_no_list, use_current_value, plan_no, report_no)
            except Exception:
                log.error(f'计划编号:[ {plan_no} ] 发生异常\n{traceback.format_exc()}')
                with app.app_context():
                    try:
                        TestPlanDao.update_running_state_by_no(plan_no, RunningState.ERROR.value)
                    except Exception:
                        log.error(f'计划编号:[ {plan_no} ] 发生异常\n{traceback.format_exc()}')

        # 先提交事务，防止新线程查询计划时拿不到
        db.session.commit()
        app = flask.current_app._get_current_object()
        # 异步执行脚本
        executor.submit(start, app, req.collectionList, req.variableSetNumberList, req.useCurrentValue)

    return {'planNo': plan_no, 'executeNow': req.executeNow}


def run_testplan(app, collection_list, set_no_list, use_current_value, plan_no, report_no=None):
    log.info(f'计划编号:[ {plan_no} ] 开始执行测试计划')
    # 记录开始时间
    start_time = timestamp_now()
    # 查询测试计划
    testplan = TestPlanDao.select_by_no(plan_no)
    # 更新运行状态
    testplan.update(RUNNING_STATE=RunningState.RUNNING.value)
    # 根据序号排序
    collection_list.sort(key=lambda k: k.serialNo)

    # 顺序执行脚本
    for collection in collection_list:
        # 根据 collectionNo 递归查询脚本数据并转换成 dict
        collection_no = collection['elementNo']
        # 查询计划项目
        plan_item = TestPlanItemDao.select_by_plan_and_collection(plan_no, collection_no)
        # 更新项目运行状态
        plan_item.update(RUNNING_STATE=RunningState.RUNNING.value)
        # 加载脚本
        collection = element_loader.loads_tree(collection_no)
        if not collection:
            log.warning(f'计划编号:[ {plan_no} ] 集合编号:[ {collection_no} ] 脚本为空或脚本已禁用，跳过当前脚本')

        # 添加自定义变量组件
        if set_no_list:
            element_loader.add_variable_data_set(collection, set_no_list, use_current_value)

        # 添加报告存储器组件
        if report_no:
            element_loader.add_flask_db_result_storage(collection, plan_no, report_no, collection_no)

        # 异步函数
        def start(app):
            try:
                log.info(f'计划编号:[ {plan_no} ] 集合名称:[ {collection["name"]} ] 开始执行脚本')
                Runner.start([collection], throw_ex=True)
            except Exception:
                log.error(f'计划编号:[ {plan_no} ] 集合编号:[ {collection_no} ] 脚本执行异常\n{traceback.format_exc()}')
                with app.app_context():
                    try:
                        plan_item.update(RUNNING_STATE=RunningState.ERROR.value)
                    except Exception:
                        log.error(f'计划编号:[ {plan_no} ] 集合编号:[ {collection_no} ] 发生异常\n{traceback.format_exc()}')

        task = executor.submit(start, app)  # 异步执行脚本
        task.result()  # 阻塞等待脚本执行完成
        # 更新项目运行状态
        plan_item.update(RUNNING_STATE=RunningState.COMPLETED.value)
        log.info(f'计划编号:[ {plan_no} ] 集合名称:[ {collection["name"]} ] 脚本执行完成')

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
    testplan.update(RUNNING_STATE=RunningState.COMPLETED.value)
    log.info(f'计划编号:[ {plan_no} ] 测试计划执行完成')
