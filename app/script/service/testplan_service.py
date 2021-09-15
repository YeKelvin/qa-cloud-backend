#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_service.py
# @Time    : 2020/3/17 14:32
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.validator import check_is_not_blank
from app.extension import db
from app.script.dao import test_element_dao as TestElementDao
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
def query_testplan_info(req):
    # 查询测试计划
    testplan = TestPlanDao.select_by_no(req.planNo)
    check_is_not_blank(testplan, '测试计划不存在')

    # 查询测试计划设置
    settings = TestPlanSettingsDao.select_by_no(req.planNo)
    check_is_not_blank(settings, '计划设置不存在')

    # 查询测试计划关联的集合
    items = TestPlanItemDao.select_all_by_plan(req.planNo)
    collectionList = []
    for item in items:
        element = TestElementDao.select_by_no(item.COLLECTION_NO)
        collectionList.append({
            'elementNo': item.COLLECTION_NO,
            'elementName': element.ELEMENT_NAME,
            'serialNo': item.SERIAL_NO
        })

    # 查询测试计划关联的变量集
    plan_set_rel_list = TestPlanVariableSetRelDao.select_all_by_plan(req.planNo)
    variableSetList = []
    for rel in plan_set_rel_list:
        set = VariableSetDao.select_by_no(rel.SET_NO)
        variableSetList.append({
            'setNo': set.SET_NO,
            'setName': set.SET_NAME
        })

    return {
        'collectionList': collectionList,
        'variableSetList': variableSetList,
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
