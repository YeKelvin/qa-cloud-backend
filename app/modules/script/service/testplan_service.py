#!/usr/bin/ python3
# @File    : testplan_service.py
# @Time    : 2020/3/17 14:32
# @Author  : Kelvin.Ye
from app.database import db_query
from app.modules.public.dao import workspace_dao
from app.modules.script.dao import test_collection_result_dao
from app.modules.script.dao import test_element_dao
from app.modules.script.dao import test_report_dao
from app.modules.script.dao import testplan_dao
from app.modules.script.dao import testplan_execution_dao
from app.modules.script.dao import testplan_execution_items_dao
from app.modules.script.dao import testplan_execution_settings_dao
from app.modules.script.dao import testplan_items_dao
from app.modules.script.dao import testplan_settings_dao
from app.modules.script.dao import variable_dataset_dao
from app.modules.script.enum import RunningState
from app.modules.script.enum import TestplanState
from app.modules.script.model import TTestplan
from app.modules.script.model import TTestplanItems
from app.modules.script.model import TTestplanSettings
from app.modules.usercenter.model import TUser
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_workspace_permission
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import datetime_now_by_utc8
from app.utils.time_util import microsecond_to_m_s


@http_service
def query_testplan_list(req):
    # 查询条件
    conds = QueryCondition(TTestplan, TUser)
    conds.like(TTestplan.WORKSPACE_NO, req.workspaceNo)
    conds.like(TTestplan.PLAN_NO, req.planNo)
    conds.like(TTestplan.PLAN_NAME, req.planName)
    conds.like(TTestplan.SCRUM_VERSION, req.scrumVersion)
    conds.like(TTestplan.SCRUM_SPRINT, req.scrumSprint)
    conds.like(TTestplan.TEST_PHASE, req.testPhase)
    conds.like(TTestplan.STATE, req.state)

    # 分页查询
    pagination = (
        db_query(
            TTestplan.PLAN_NO,
            TTestplan.PLAN_NAME,
            TTestplan.PLAN_DESC,
            TTestplan.COLLECTION_TOTAL,
            TTestplan.SCRUM_VERSION,
            TTestplan.SCRUM_SPRINT,
            TTestplan.TEST_PHASE,
            TTestplan.STATE,
            TTestplan.START_TIME,
            TTestplan.END_TIME,
            TTestplan.CREATED_BY,
            TTestplan.CREATED_TIME,
            TUser.USER_NAME
        )
        .outerjoin(TUser, TTestplan.CREATED_BY == TUser.USER_NO)
        .filter(*conds)
        .order_by(TTestplan.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )
    for item in pagination.items:
        print(item)

    data = [
        {
            'planNo': item.PLAN_NO,
            'planName': item.PLAN_NAME,
            'planDesc': item.PLAN_DESC,
            'collectionTotal': item.COLLECTION_TOTAL,
            'scrumVersion': item.SCRUM_VERSION,
            'scrumSprint': item.SCRUM_SPRINT,
            'testPhase': item.TEST_PHASE,
            'state': item.STATE,
            'startTime': item.START_TIME.strftime('%Y-%m-%d %H:%M:%S') if item.START_TIME else None,
            'endTime': item.END_TIME.strftime('%Y-%m-%d %H:%M:%S') if item.END_TIME else None,
            'createdBy': item.USER_NAME,
            'createdTime':item.CREATED_TIME.strftime('%Y-%m-%d %H:%M:%S')
        }
        for item in pagination.items
    ]

    return {'data': data, 'total': pagination.total}


@http_service
def query_testplan_all(req):
    conds = QueryCondition()
    conds.equal(TTestplan.WORKSPACE_NO, req.workspaceNo)
    conds.in_(TTestplan.STATE, req.stateList)
    testplans = TTestplan.filter(*conds).order_by(TTestplan.CREATED_TIME.desc()).all()

    return [
        {
            'planNo': testplan.PLAN_NO,
            'planName': testplan.PLAN_NAME,
            'planDesc': testplan.PLAN_DESC,
            'scrumSprint': testplan.SCRUM_SPRINT,
            'scrumVersion': testplan.SCRUM_VERSION,
            'collectionTotal': testplan.COLLECTION_TOTAL,
            'state': testplan.STATE,
            'testPhase': testplan.TEST_PHASE
        }
        for testplan in testplans
    ]


@http_service
def query_testplan(req):
    # 查询测试计划
    testplan = testplan_dao.select_by_no(req.planNo)
    check_exists(testplan, error_msg='测试计划不存在')

    # 查询测试计划设置项
    settings = testplan_settings_dao.select_by_no(req.planNo)
    check_exists(settings, error_msg='计划设置不存在')

    # 查询测试计划关联的集合
    items = testplan_items_dao.select_all_by_plan(req.planNo)
    collections = [item.COLLECTION_NO for item in items]

    return {
        'planNo': testplan.PLAN_NO,
        'planName': testplan.PLAN_NAME,
        'planDesc': testplan.PLAN_DESC,
        'scrumVersion': testplan.SCRUM_VERSION,
        'scrumSprint': testplan.SCRUM_SPRINT,
        'concurrency': settings.CONCURRENCY,
        'iterations': settings.ITERATIONS,
        'delay': settings.DELAY,
        'save': settings.SAVE,
        'saveOnError': settings.SAVE_ON_ERROR,
        'stopOnErrorCount': settings.STOP_ON_ERROR_COUNT,
        'notificationRobots': settings.NOTIFICATION_ROBOTS,
        'collections': collections
    }


@http_service
def create_testplan(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 查询工作空间
    workspace = workspace_dao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')

    # 创建计划编号
    plan_no = new_id()

    # 新增测试计划设置项
    TTestplanSettings.insert(
        PLAN_NO=plan_no,
        CONCURRENCY=req.concurrency,
        ITERATIONS=req.iterations,
        DELAY=req.delay,
        SAVE=req.save,
        SAVE_ON_ERROR=req.saveOnError,
        NOTIFICATION_ROBOTS=req.notificationRobots,
        STOP_ON_ERROR_COUNT=req.stopOnErrorCount
    )

    # 新增测试计划项目明细
    for collection in req.collectionList:
        TTestplanItems.insert(
            PLAN_NO=plan_no,
            COLLECTION_NO=collection.elementNo,
            COLLECTION_SORT=collection.elementIndex
        )

    # 新增测试计划
    TTestplan.insert(
        WORKSPACE_NO=req.workspaceNo,
        PLAN_NO=plan_no,
        PLAN_NAME=req.planName,
        PLAN_DESC=req.planDesc,
        SCRUM_SPRINT=req.scrumSprint,
        SCRUM_VERSION=req.scrumVersion,
        COLLECTION_TOTAL=len(req.collectionList),
        STATE=TestplanState.INITIAL.value
    )

    return {'planNo': plan_no}


@http_service
def modify_testplan(req):
    # 查询测试计划
    testplan = testplan_dao.select_by_no(req.planNo)
    check_exists(testplan, error_msg='测试计划不存在')

    # 校验空间权限
    check_workspace_permission(testplan.WORKSPACE_NO)

    # 查询测试计划设置项
    settings = testplan_settings_dao.select_by_no(req.planNo)
    check_exists(settings, error_msg='计划设置不存在')

    # 修改测试计划项目明细
    collections = []
    for collection in req.collectionList:
        collections.append(collection.elementNo)
        # 查询测试计划关联的集合
        if item := testplan_items_dao.select_by_plan_and_collection(req.planNo, collection.elementNo):
            item.update(COLLECTION_SORT=collection.elementIndex)
        else:
            TTestplanItems.insert(
                PLAN_NO=req.planNo,
                COLLECTION_NO=collection.elementNo,
                COLLECTION_SORT=collection.elementIndex
            )
    # 删除不在请求中的集合
    testplan_items_dao.delete_all_by_plan_and_not_in_collection(req.planNo, collections)

    # 修改测试计划
    testplan.update(
        PLAN_NAME=req.planName,
        PLAN_DESC=req.planDesc,
        SCRUM_SPRINT=req.scrumSprint,
        SCRUM_VERSION=req.scrumVersion,
        COLLECTION_TOTAL=len(req.collectionList)
    )

    # 修改测试计划设置项项
    settings.update(
        CONCURRENCY=req.concurrency,
        ITERATIONS=req.iterations,
        DELAY=req.delay,
        SAVE=req.save,
        SAVE_ON_ERROR=req.saveOnError,
        STOP_ON_ERROR_COUNT=req.stopOnErrorCount
    )


@http_service
def modify_testplan_state(req):
    # 查询测试计划
    testplan = testplan_dao.select_by_no(req.planNo)
    check_exists(testplan, error_msg='测试计划不存在')

    # 校验空间权限
    check_workspace_permission(testplan.WORKSPACE_NO)

    # 更新计划状态
    if req.state == TestplanState.TESTING.value and not testplan.START_TIME:
        testplan.update(STATE=req.state, START_TIME=datetime_now_by_utc8())
    elif req.state == TestplanState.COMPLETED.value:
        testplan.update(STATE=req.state, END_TIME=datetime_now_by_utc8())
    else:
        testplan.update(STATE=req.state)


@http_service
def modify_testplan_testphase(req):
    # 查询测试计划
    testplan = testplan_dao.select_by_no(req.planNo)
    check_exists(testplan, error_msg='测试计划不存在')
    # 校验空间权限
    check_workspace_permission(testplan.WORKSPACE_NO)
    # 更新测试阶段
    testplan.update(TEST_PHASE=req.testPhase)


@http_service
def query_testplan_execution_all(req):
    # 查询测试计划
    testplan = testplan_dao.select_by_no(req.planNo)
    check_exists(testplan, error_msg='测试计划不存在')

    # 查询所有执行记录
    executions = testplan_execution_dao.select_all_by_plan(req.planNo)
    result = []
    for execution in executions:
        report = test_report_dao.select_by_execution(execution.EXECUTION_NO)
        result.append({
            'executionNo': execution.EXECUTION_NO,
            'runningState': execution.RUNNING_STATE,
            'environment': execution.ENVIRONMENT,
            'testPhase': execution.TEST_PHASE,
            'reportNo': report.REPORT_NO if report else None,
            'startTime': execution.START_TIME.strftime('%Y-%m-%d %H:%M:%S') if execution.START_TIME else 0,
            'endTime': execution.END_TIME.strftime('%Y-%m-%d %H:%M:%S') if execution.END_TIME else 0,
        })
    return result


@http_service
def query_testplan_execution_details(req):
    # 查询执行记录
    execution = testplan_execution_dao.select_by_no(req.executionNo)
    check_exists(execution, error_msg='执行记录不存在')

    # 查询执行记录设置项
    settings = testplan_execution_settings_dao.select_by_no(req.executionNo)
    check_exists(settings, error_msg='计划设置不存在')

    # 查询测试报告，如果没有勾选保存结果就没有测试报告
    report = test_report_dao.select_by_execution(execution.EXECUTION_NO)

    # 查询执行记录关联的集合
    items = testplan_execution_items_dao.select_all_by_execution(req.executionNo)
    collection_list = []
    for item in items:
        result = None
        if report:
            result = test_collection_result_dao.select_by_report_and_collectionno(report.REPORT_NO, item.COLLECTION_NO)
        collection = None
        if not result:
            collection = test_element_dao.select_by_no(item.COLLECTION_NO)
        collection_list.append({
            'elementNo': item.COLLECTION_NO,
            'elementName': result.COLLECTION_NAME if result else collection.ELEMENT_NAME,
            'elementDesc': result.COLLECTION_DESC if result else collection.ELEMENT_DESC,
            'runningState': item.RUNNING_STATE,
            'success': (
                result.SUCCESS
                if result and item.RUNNING_STATE not in (RunningState.WAITING.value, RunningState.RUNNING.value)
                else None
            ),
            'startTime': result.START_TIME.strftime('%Y-%m-%d %H:%M:%S') if result and result.START_TIME else None,
            'endTime': result.END_TIME.strftime('%Y-%m-%d %H:%M:%S') if result and result.END_TIME else None,
            'elapsedTime': microsecond_to_m_s(result.ELAPSED_TIME) if result and result.ELAPSED_TIME else None,
            'iterationCount': item.ITERATION_COUNT,
            'successCount': item.SUCCESS_COUNT,
            'failureCount': item.FAILURE_COUNT,
            'errorCount': item.ERROR_COUNT
        })

    # 查询执行记录关联的变量集
    variable_dataset_list = []
    if settings.VARIABLE_DATASETS:
        for dataset_no in settings.VARIABLE_DATASETS:
            dataset = variable_dataset_dao.select_by_number_with_deleted(dataset_no)
            dataset and variable_dataset_list.append({
                'datasetNo': dataset.DATASET_NO,
                'datasetName': dataset.DATASET_NAME
            })

    return {
        'collectionList': collection_list,
        'datasetList': variable_dataset_list,
        'concurrency': settings.CONCURRENCY,
        'iterations': settings.ITERATIONS,
        'delay': settings.DELAY,
        'save': settings.SAVE,
        'saveOnError': settings.SAVE_ON_ERROR,
        'stopOnErrorCount': settings.STOP_ON_ERROR_COUNT,
        'useCurrentValue': settings.USE_CURRENT_VALUE,
        'iterationCount': execution.ITERATION_COUNT,
        'interrupt': execution.INTERRUPT,
        'interruptBy': execution.INTERRUPT_BY,
        'interruptTime': execution.INTERRUPT_TIME,
        'reportNo': report.REPORT_NO if report else None
    }
