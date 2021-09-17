#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_service.py
# @Time    : 2020/3/17 14:32
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.validator import check_is_not_blank
from app.extension import db
from app.script.dao import test_collection_result_dao as TestCollectionResultDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.dao import test_group_result_dao as TestGroupResultDao
from app.script.dao import test_report_dao as TestReportDao
from app.script.dao import test_sampler_result_dao as TestSamplerResultDao
from app.script.dao import testplan_dao as TestPlanDao
from app.script.dao import testplan_item_dao as TestPlanItemDao
from app.script.dao import testplan_settings_dao as TestPlanSettingsDao
from app.script.dao import testplan_variable_set_rel_dao as TestPlanVariableSetRelDao
from app.script.dao import variable_set_dao as VariableSetDao
from app.script.model import TTestPlan
from app.utils.log_util import get_logger
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_testplan_list(req):
    # 查询条件
    conds = QueryCondition(TTestPlan)
    conds.fuzzy_match(TTestPlan.WORKSPACE_NO, req.workspaceNo)
    conds.fuzzy_match(TTestPlan.VERSION_NO, req.versionNo)
    conds.fuzzy_match(TTestPlan.PLAN_NO, req.planNo)
    conds.fuzzy_match(TTestPlan.PLAN_NAME, req.planName)
    conds.fuzzy_match(TTestPlan.RUNNING_STATE, req.runningState)

    # 分页查询
    pagination = db.session.query(
        TTestPlan).filter(*conds).order_by(TTestPlan.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for item in pagination.items:
        data.append({
            'versionNo': item.VERSION_NO,
            'planNo': item.PLAN_NO,
            'planName': item.PLAN_NAME,
            'planDesc': item.PLAN_DESC,
            'total': item.TOTAL,
            'runningState': item.RUNNING_STATE
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_testplan_all(req):
    pass


@http_service
def query_testplan_details(req):
    # 查询测试计划
    testplan = TestPlanDao.select_by_no(req.planNo)
    check_is_not_blank(testplan, '测试计划不存在')

    # 查询测试计划设置
    settings = TestPlanSettingsDao.select_by_no(req.planNo)
    check_is_not_blank(settings, '计划设置不存在')

    # 查询测试计划关联的集合
    items = TestPlanItemDao.select_all_by_plan(req.planNo)
    collection_list = []
    for item in items:
        element = TestElementDao.select_by_no(item.COLLECTION_NO)
        collection_list.append({
            'elementNo': item.COLLECTION_NO,
            'elementName': element.ELEMENT_NAME,
            'serialNo': item.SERIAL_NO
        })

    # 查询测试计划关联的变量集
    plan_set_rel_list = TestPlanVariableSetRelDao.select_all_by_plan(req.planNo)
    variable_set_list = []
    for rel in plan_set_rel_list:
        variable_set = VariableSetDao.select_by_no(rel.SET_NO)
        variable_set_list.append({'setNo': variable_set.SET_NO, 'setName': variable_set.SET_NAME})

    return {
        'collectionList': collection_list,
        'variableSetList': variable_set_list,
        'versionNo': testplan.VERSION_NO,
        'planNo': testplan.PLAN_NO,
        'planName': testplan.PLAN_NAME,
        'planDesc': testplan.PLAN_DESC,
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
            'collectionNo': collection_result.COLLECTION_NO,
            'collectionId': collection_result.COLLECTION_ID,
            'collectionName': collection_result.COLLECTION_NAME,
            'collectionRemark': collection_result.COLLECTION_REMARK,
            'startTime': collection_result.START_TIME,
            'endTime': collection_result.END_TIME,
            'elapsedTime': collection_result.ELAPSED_TIME,
            'success': collection_result.SUCCESS,
            'groups': get_groups_result(collection_result.COLLECTION_ID)
        })
    return {
        'details': {
            'reportName': report.REPORT_NAME,
            'reportDesc': report.REPORT_DESC,
            'startTime': report.START_TIME,
            'endTime': report.END_TIME,
            'elapsedTime': report.ELAPSED_TIME
        },
        'collections': collections
    }


def get_groups_result(collection_id):
    groups = []
    group_result_list = TestGroupResultDao.select_all_by_collection(collection_id)
    for group_result in group_result_list:
        groups.append({
            'collectionId': group_result.COLLECTION_ID,
            'groupId': group_result.GROUP_ID,
            'groupName': group_result.GROUP_NAME,
            'groupRemark': group_result.GROUP_REMARK,
            'startTime': group_result.START_TIME,
            'endTime': group_result.END_TIME,
            'elapsedTime': group_result.ELAPSED_TIME,
            'success': group_result.SUCCESS,
            'samplers': get_samplers_result(group_result.GROUP_ID)
        })
    return groups


def get_samplers_result(group_id):
    samplers = []
    sampler_result_list = TestSamplerResultDao.select_all_by_group(group_id)
    for sampler_result in sampler_result_list:
        samplers.append({
            'samplerId': sampler_result.SAMPLER_ID,
            'samplerName': sampler_result.SAMPLER_NAME,
            'samplerRemark': sampler_result.SAMPLER_REMARK,
            'startTime': sampler_result.START_TIME,
            'endTime': sampler_result.END_TIME,
            'elapsedTime': sampler_result.ELAPSED_TIME,
            'success': sampler_result.SUCCESS,
            'requestUrl': sampler_result.REQUEST_URL,
            'requestHeaders': sampler_result.REQUEST_HEADERS,
            'requestData': sampler_result.REQUEST_DATA,
            'responseCode': sampler_result.RESPONSE_CODE,
            'responseHeaders': sampler_result.RESPONSE_HEADERS,
            'responseData': sampler_result.RESPONSE_DATA,
            'errorAssertion': sampler_result.ERROR_ASSERTION,
            'subSamplers': get_subsamplers_result(sampler_result.SAMPLER_ID)
        })
    return samplers


def get_subsamplers_result(parent_id):
    sub_samplers = []
    sub_sampler_result_list = TestSamplerResultDao.select_all_by_parent(parent_id)
    for sub_result in sub_sampler_result_list:
        sub_samplers.append({
            'samplerId': sub_result.SAMPLER_ID,
            'samplerName': sub_result.SAMPLER_NAME,
            'samplerRemark': sub_result.SAMPLER_REMARK,
            'startTime': sub_result.START_TIME,
            'endTime': sub_result.END_TIME,
            'elapsedTime': sub_result.ELAPSED_TIME,
            'success': sub_result.SUCCESS,
            'requestUrl': sub_result.REQUEST_URL,
            'requestHeaders': sub_result.REQUEST_HEADERS,
            'requestData': sub_result.REQUEST_DATA,
            'responseCode': sub_result.RESPONSE_CODE,
            'responseHeaders': sub_result.RESPONSE_HEADERS,
            'responseData': sub_result.RESPONSE_DATA,
            'errorAssertion': sub_result.ERROR_ASSERTION,
            'subSamplers': get_subsamplers_result(sub_result.SAMPLER_ID)
        })
    return sub_samplers
