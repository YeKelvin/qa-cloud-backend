#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_service.py
# @Time    : 2020/3/17 14:32
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.id_generator import new_id
from app.common.validator import check_is_not_blank
from app.extension import db
from app.public.dao import workspace_dao as WorkspaceDao
from app.script.dao import test_collection_result_dao as TestCollectionResultDao
from app.script.dao import test_report_dao as TestReportDao
from app.script.dao import testplan_dao as TestPlanDao
from app.script.dao import testplan_dataset_rel_dao as TestPlanDatasetRelDao
from app.script.dao import testplan_execution_dao as TestplanExecutionDao
from app.script.dao import testplan_execution_items_dao as TestPlanExecutionItemsDao
from app.script.dao import testplan_execution_settings_dao as TestPlanExecutionSettingsDao
from app.script.dao import testplan_items_dao as TestPlanItemsDao
from app.script.dao import testplan_settings_dao as TestPlanSettingsDao
from app.script.dao import variable_dataset_dao as VariableDatasetDao
from app.script.enum import TestPhase
from app.script.enum import TestplanState
from app.script.enum import VariableDatasetType
from app.script.model import TTestplan
from app.script.model import TTestplanDatasetRel
from app.script.model import TTestplanItems
from app.script.model import TTestplanSettings
from app.utils.json_util import from_json
from app.utils.log_util import get_logger
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import microsecond_to_m_s


log = get_logger(__name__)


@http_service
def query_testplan_list(req):
    # 查询条件
    conds = QueryCondition(TTestplan)
    conds.like(TTestplan.WORKSPACE_NO, req.workspaceNo)
    conds.like(TTestplan.PLAN_NO, req.planNo)
    conds.like(TTestplan.PLAN_NAME, req.planName)
    conds.like(TTestplan.VERSION_NUMBER, req.versionNumber)
    conds.like(TTestplan.ENVIRONMENT, req.environment)
    conds.like(TTestplan.STATE, req.state)
    conds.like(TTestplan.TEST_PHASE, req.testPhase)

    # 分页查询
    pagination = db.session.query(
        TTestplan).filter(*conds).order_by(TTestplan.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for item in pagination.items:
        data.append({
            'planNo': item.PLAN_NO,
            'planName': item.PLAN_NAME,
            'planDesc': item.PLAN_DESC,
            'versionNumber': item.VERSION_NUMBER,
            'environment': item.ENVIRONMENT,
            'collectionTotal': item.COLLECTION_TOTAL,
            'testPhase': item.TEST_PHASE,
            'state': item.STATE,
            'startTime': item.START_TIME,
            'endTime': item.END_TIME,
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_testplan(req):
    # 查询测试计划
    testplan = TestPlanDao.select_by_no(req.planNo)
    check_is_not_blank(testplan, '测试计划不存在')

    # 查询测试计划设置项
    settings = TestPlanSettingsDao.select_by_no(req.planNo)
    check_is_not_blank(settings, '计划设置不存在')

    # 查询测试计划关联的集合
    items = TestPlanItemsDao.select_all_by_plan(req.planNo)
    collection_number_list = [item.COLLECTION_NO for item in items]

    # 查询测试计划关联的变量集
    plan_dataset_rel_list = TestPlanDatasetRelDao.select_all_by_plan(req.planNo)
    dataset_number_list = [rel.DATASET_NO for rel in plan_dataset_rel_list]

    return {
        'planNo': testplan.PLAN_NO,
        'planName': testplan.PLAN_NAME,
        'planDesc': testplan.PLAN_DESC,
        'versionNumber': testplan.VERSION_NUMBER,
        'concurrency': settings.CONCURRENCY,
        'iterations': settings.ITERATIONS,
        'delay': settings.DELAY,
        'save': settings.SAVE,
        'saveOnError': settings.SAVE_ON_ERROR,
        'stopTestOnErrorCount': settings.STOP_TEST_ON_ERROR_COUNT,
        'useCurrentValue': settings.USE_CURRENT_VALUE,
        'collectionNumberList': collection_number_list,
        'datasetNumberList': dataset_number_list
    }


@http_service
@transactional
def create_testplan(req):
    # 查询工作空间
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_is_not_blank(workspace, '工作空间不存在')

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
        STOP_TEST_ON_ERROR_COUNT=req.stopTestOnErrorCount,
        USE_CURRENT_VALUE=req.useCurrentValue,
    )

    # 新增测试计划与数据集关联
    environment = ''
    for dataset_no in req.datasetNumberList:
        dataset = VariableDatasetDao.select_by_no(dataset_no)
        if dataset.DATASET_TYPE == VariableDatasetType.ENVIRONMENT.value:
            environment = dataset.DATASET_NAME
        TTestplanDatasetRel.insert(
            PLAN_NO=plan_no,
            DATASET_NO=dataset_no
        )

    # 新增测试计划项目明细
    for collection in req.collectionList:
        TTestplanItems.insert(
            PLAN_NO=plan_no,
            COLLECTION_NO=collection.elementNo,
            SERIAL_NO=collection.serialNo
        )

    # 新增测试计划
    TTestplan.insert(
        WORKSPACE_NO=req.workspaceNo,
        PLAN_NO=plan_no,
        PLAN_NAME=req.planName,
        PLAN_DESC=req.planDesc,
        VERSION_NUMBER=req.versionNumber,
        ENVIRONMENT=environment,
        COLLECTION_TOTAL=len(req.collectionList),
        TEST_PHASE=TestPhase.INITIAL.value,
        STATE=TestplanState.INITIAL.value
    )

    return {'planNo': plan_no}


@http_service
@transactional
def modify_testplan(req):
    # 查询测试计划
    testplan = TestPlanDao.select_by_no(req.planNo)
    check_is_not_blank(testplan, '测试计划不存在')

    # 查询测试计划设置项
    settings = TestPlanSettingsDao.select_by_no(req.planNo)
    check_is_not_blank(settings, '计划设置不存在')

    # 修改测试计划与数据集关联
    environment = ''
    for dataset_no in req.datasetNumberList:
        # 查询变量集
        dataset = VariableDatasetDao.select_by_no(dataset_no)
        if dataset.DATASET_TYPE == VariableDatasetType.ENVIRONMENT.value:
            environment = dataset.DATASET_NAME
        # 查询测试计划关联的变量集
        plan_dataset_rel = TestPlanDatasetRelDao.select_by_plan_and_dataset(req.planNo, dataset_no)
        # 不存在则新增
        if not plan_dataset_rel:
            TTestplanDatasetRel.insert(PLAN_NO=req.planNo, DATASET_NO=dataset_no)
    # 删除不在请求中的数据集关联
    TestPlanDatasetRelDao.delete_all_by_plan_and_not_in_dataset(req.planNo, req.datasetNumberList)

    # 修改测试计划项目明细
    collection_no_list = []
    for collection in req.collectionList:
        collection_no_list.append(collection.elementNo)
        # 查询测试计划关联的集合
        item = TestPlanItemsDao.select_by_plan_and_collection(req.planNo, collection)
        if item:
            item.update(SERIAL_NO=collection.serialNo)
        else:
            TTestplanItems.insert(
                PLAN_NO=req.planNo,
                COLLECTION_NO=collection.elementNo,
                SERIAL_NO=collection.serialNo
            )
    # 删除不在请求中的集合
    TestPlanItemsDao.delete_all_by_plan_and_not_in_collection(req.planNo, collection_no_list)

    # 修改测试计划
    testplan.update(
        PLAN_NAME=req.planName,
        PLAN_DESC=req.planDesc,
        VERSION_NUMBER=req.versionNumber,
        ENVIRONMENT=environment,
        COLLECTION_TOTAL=len(req.collectionList)
    )

    # 修改测试计划设置项项
    settings.update(
        CONCURRENCY=req.concurrency,
        ITERATIONS=req.iterations,
        DELAY=req.delay,
        SAVE=req.save,
        SAVE_ON_ERROR=req.saveOnError,
        STOP_TEST_ON_ERROR_COUNT=req.stopTestOnErrorCount,
        USE_CURRENT_VALUE=req.useCurrentValue,
    )


@http_service
def modify_testplan_state(req):
    # 查询测试计划
    testplan = TestPlanDao.select_by_no(req.planNo)
    check_is_not_blank(testplan, '测试计划不存在')
    testplan.update(STATE=TestplanState.INITIAL.value)


@http_service
def modify_testplan_testphase(req):
    # 查询测试计划
    testplan = TestPlanDao.select_by_no(req.planNo)
    check_is_not_blank(testplan, '测试计划不存在')
    testplan.update(TEST_PHASE=TestPhase.INITIAL.value)


@http_service
def query_testplan_execution_all(req):
    # 查询测试计划
    testplan = TestPlanDao.select_by_no(req.planNo)
    check_is_not_blank(testplan, '测试计划不存在')

    # 查询所有执行记录
    executions = TestplanExecutionDao.select_all_by_plan(req.planNo)
    result = []
    for execution in executions:
        report = TestReportDao.select_by_execution(execution.EXECUTION_NO)
        result.append({
            'executionNo': execution.EXECUTION_NO,
            'runningState': execution.RUNNING_STATE,
            'createdTime': execution.CREATED_TIME,
            'reportNo': report.REPORT_NO if report else None
        })
    return result


@http_service
def query_testplan_execution_details(req):
    # 查询执行记录
    execution = TestplanExecutionDao.select_by_no(req.executionNo)
    check_is_not_blank(execution, '执行记录不存在')

    # 查询执行记录设置项
    settings = TestPlanExecutionSettingsDao.select_by_no(req.executionNo)
    check_is_not_blank(settings, '计划设置不存在')

    # 查询测试报告
    report = TestReportDao.select_by_execution(execution.EXECUTION_NO)

    # 查询测试计划关联的集合
    items = TestPlanExecutionItemsDao.select_all_by_execution(req.executionNo)
    collection_list = []
    for item in items:
        result = TestCollectionResultDao.select_by_report_and_collectionno(report.REPORT_NO, item.COLLECTION_NO)
        collection_list.append({
            'elementNo': item.COLLECTION_NO,
            'elementName': result.COLLECTION_NAME,
            'elementRemark': result.COLLECTION_REMARK,
            'runningState': item.RUNNING_STATE,
            'success': result.SUCCESS,
            'startTime': result.START_TIME,
            'endTime': result.END_TIME,
            'elapsedTime': microsecond_to_m_s(result.ELAPSED_TIME)
        })

    # 查询测试计划关联的变量集
    dataset_number_list = from_json(settings.DATASETS)
    dataset_list = []
    for dataset_no in dataset_number_list:
        dataset = VariableDatasetDao.select_by_no(dataset_no)
        dataset_list.append({'datasetNo': dataset.DATASET_NO, 'datasetName': dataset.DATASET_NAME})

    return {
        'collectionList': collection_list,
        'datasetList': dataset_list,
        'concurrency': settings.CONCURRENCY,
        'iterations': settings.ITERATIONS,
        'delay': settings.DELAY,
        'save': settings.SAVE,
        'saveOnError': settings.SAVE_ON_ERROR,
        'stopTestOnErrorCount': settings.STOP_TEST_ON_ERROR_COUNT,
        'useCurrentValue': settings.USE_CURRENT_VALUE,
        'reportNo': report.REPORT_NO if report else None
    }
