#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_service.py
# @Time    : 2020/3/17 14:32
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.id_generator import new_id
from app.common.validator import check_is_not_blank
from app.extension import db
from app.public.dao import workspace_dao as WorkspaceDao
from app.script.dao import test_collection_result_dao as TestCollectionResultDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.dao import test_group_result_dao as TestGroupResultDao
from app.script.dao import test_report_dao as TestReportDao
from app.script.dao import test_sampler_result_dao as TestSamplerResultDao
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
from app.script.model import TTestplan
from app.script.model import TTestplanDatasetRel
from app.script.model import TTestplanItems
from app.script.model import TTestplanSettings
from app.utils.log_util import get_logger
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import microsecond_to_h_m_s
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
    collection_list = []
    for item in items:
        element = TestElementDao.select_by_no(item.COLLECTION_NO)
        collection_list.append({
            'elementNo': item.COLLECTION_NO,
            'elementName': element.ELEMENT_NAME,
            'serialNo': item.SERIAL_NO
        })

    # 查询测试计划关联的变量集
    plan_dataset_rel_list = TestPlanDatasetRelDao.select_all_by_plan(req.planNo)
    dataset_list = []
    for rel in plan_dataset_rel_list:
        dataset = VariableDatasetDao.select_by_no(rel.DATASET_NO)
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
        'useCurrentValue': settings.USE_CURRENT_VALUE
    }


@http_service
def create_testplan(req):
    # 查询工作空间
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_is_not_blank(workspace, '工作空间不存在')

    # 新增测试计划
    plan_no = new_id()
    TTestplan.insert(
        WORKSPACE_NO=req.workspaceNo,
        PLAN_NO=plan_no,
        PLAN_NAME=req.planName,
        PLAN_DESC=req.planDesc,
        VERSION_NUMBER=req.versionNo,
        ENVIRONMENT=req.environment,
        TEST_PHASE=TestPhase.INITIAL.value,
        STATE=TestplanState.INITIAL.value
    )

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
    for dataset_no in req.datasetNumberList:
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

    return {'planNo': plan_no}


@http_service
def modify_testplan(req):
    # 查询测试计划
    testplan = TestPlanDao.select_by_no(req.planNo)
    check_is_not_blank(testplan, '测试计划不存在')

    # 查询测试计划设置项
    settings = TestPlanSettingsDao.select_by_no(req.planNo)
    check_is_not_blank(settings, '计划设置不存在')

    # 修改测试计划
    testplan.update(
        PLAN_NAME=req.planName,
        PLAN_DESC=req.planDesc,
        VERSION_NUMBER=req.versionNo,
        ENVIRONMENT=req.environment
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

    # 修改测试计划与数据集关联
    for dataset_no in req.datasetNumberList:
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
    TestPlanItemsDao.delete_all_by_plan_and_not_in_dataset(req.planNo, collection_no_list)


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
        result.append({
            'executionNo': execution.EXECUTION_NO,
            'runningState': execution.RUNNING_STATE,
            'createdTime': execution.CREATED_TIME
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

    # 查询测试计划关联的集合
    items = TestPlanExecutionItemsDao.select_all_by_execution(req.executionNo)
    collection_list = []
    for item in items:
        element = TestElementDao.select_by_no(item.COLLECTION_NO)
        collection_list.append({
            'elementNo': item.COLLECTION_NO,
            'elementName': element.ELEMENT_NAME,
            'runningState': item.RUNNING_STATE
        })

    # 查询测试计划关联的变量集
    # plan_set_rel_list = TestPlanDatasetRelDao.select_all_by_plan(req.planNo)
    # variable_set_list = []
    # for rel in plan_set_rel_list:
    #     variable_set = VariableDatasetDao.select_by_no(rel.DATASET_NO)
    #     variable_set_list.append({'datasetNo': variable_set.DATASET_NO, 'datasetName': variable_set.DATASET_NAME})

    return {
        'collectionList': collection_list,
        # 'datasetList': variable_set_list,
        'concurrency': settings.CONCURRENCY,
        'iterations': settings.ITERATIONS,
        'delay': settings.DELAY,
        'save': settings.SAVE,
        'saveOnError': settings.SAVE_ON_ERROR,
        'stopTestOnErrorCount': settings.STOP_TEST_ON_ERROR_COUNT,
        'useCurrentValue': settings.USE_CURRENT_VALUE
    }


@http_service
def query_testplan_report(req):
    # 查询测试计划
    testplan = TestPlanDao.select_by_no(req.planNo)
    check_is_not_blank(testplan, '测试计划不存在')

    # 查询测试报告
    report = TestReportDao.select_by_plan(req.planNo)

    # 递归查询脚本结果
    collections = []
    collection_result_list = TestCollectionResultDao.select_all_by_report(report.REPORT_NO)
    for collection_result in collection_result_list:
        collections.append({
            'reportNo': collection_result.REPORT_NO,
            'elementNo': collection_result.COLLECTION_NO,
            'id': collection_result.COLLECTION_ID,
            'name': collection_result.COLLECTION_NAME,
            'remark': collection_result.COLLECTION_REMARK,
            'startTime': collection_result.START_TIME.strftime('%H:%M:%S'),
            'endTime': collection_result.END_TIME.strftime('%H:%M:%S'),
            'elapsedTime': microsecond_to_m_s(collection_result.ELAPSED_TIME),
            'success': collection_result.SUCCESS,
        })

    return {
        'details': {
            'reportName': report.REPORT_NAME,
            'reportDesc': report.REPORT_DESC,
            'startTime': report.START_TIME.strftime('%Y-%m-%d %H:%M:%S'),
            'endTime': report.END_TIME.strftime('%Y-%m-%d %H:%M:%S'),
            'elapsedTime': microsecond_to_h_m_s(report.ELAPSED_TIME),
            'successfulCollectionsTotal': TestCollectionResultDao.count_by_report_and_success(report.REPORT_NO, True),
            'successfulGroupsTotal': TestGroupResultDao.count_by_report_and_success(report.REPORT_NO, True),
            'successfulSamplersTotal': TestSamplerResultDao.count_by_report_and_success(report.REPORT_NO, True),
            'failedCollectionsTotal': TestCollectionResultDao.count_by_report_and_success(report.REPORT_NO, False),
            'failedGroupsTotal': TestGroupResultDao.count_by_report_and_success(report.REPORT_NO, False),
            'failedSamplersTotal': TestSamplerResultDao.count_by_report_and_success(report.REPORT_NO, False),
            'avgCollectionsElapsedTime': microsecond_to_m_s(
                TestCollectionResultDao.avg_elapsed_time_by_report(report.REPORT_NO)
            ),
            'avgGroupsElapsedTime': microsecond_to_m_s(
                TestGroupResultDao.avg_elapsed_time_by_report(report.REPORT_NO)
            ),
            'avgSamplersElapsedTime': f'{TestSamplerResultDao.avg_elapsed_time_by_report(report.REPORT_NO)}ms',
        },
        'collections': collections
    }
