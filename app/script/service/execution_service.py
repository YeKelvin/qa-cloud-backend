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
from app.script.dao import element_builtin_child_rel_dao as ElementBuiltinChildRelDao
from app.script.dao import element_child_rel_dao as ElementChildRelDao
from app.script.dao import element_property_dao as ElementPropertyDao
from app.script.dao import http_header_dao as HttpHeaderDao
from app.script.dao import http_sampler_headers_rel_dao as HttpSamplerHeadersRelDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.dao import test_report_dao as TestReportDao
from app.script.dao import testplan_dao as TestPlanDao
from app.script.dao import testplan_item_dao as TestPlanItemDao
from app.script.dao import variable_dao as VariableDao
from app.script.dao import variable_set_dao as VariableSetDao
from app.script.enum import ElementClass
from app.script.enum import ElementType
from app.script.enum import RunningState
from app.script.model import TTestElement
from app.script.model import TTestPlan
from app.script.model import TTestPlanItem
from app.script.model import TTestPlanSettings
from app.script.model import TTestPlanVariableSetRel
from app.script.model import TTestReport
from app.utils.json_util import from_json
from app.utils.log_util import get_logger
from app.utils.time_util import timestamp_now
from app.utils.time_util import timestamp_to_utc8_datetime


log = get_logger(__name__)


@http_service
def execute_collection(req):
    # 根据 collectionNo 递归查询脚本数据并转换成 dict
    collection = load_element_tree(req.collectionNo)
    if not collection:
        raise ServiceError('脚本为空或脚本已禁用，请检查脚本后重新运行')

    # 添加 socket 组件
    if req.socketId:
        add_flask_socketio_result_collector(collection, req.socketId)

    # 添加变量组件
    if req.variableSet:
        add_variable_data_set(collection, req.variableSet.numberList, req.variableSet.useCurrentValue)

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


def load_element_tree(element_no):
    # 查询元素
    element = TestElementDao.select_by_no(element_no)
    check_is_not_blank(element, '元素不存在')

    # 元素为禁用状态时返回 None
    if not element.ENABLED:
        log.info(f'元素:[ {element.ELEMENT_NAME} ] 已禁用，不需要添加至脚本')
        return None

    # 元素子代
    children = []

    # 读取元素属性
    property = load_element_property(element_no)

    # 如果是 HttpSampler 则添加 HTTP 请求头管理器
    if element.ELEMENT_CLASS == ElementClass.HTTP_SAMPLER.value:
        add_http_header_manager(element, children)

    # 普通 Sampler 正常添加子代元素
    if element.ELEMENT_CLASS != ElementClass.SNIPPET_SAMPLER.value:
        # 递归查询元素子代，并根据序号正序排序
        child_rel_list = ElementChildRelDao.select_all_by_parent(element_no)

        # 添加元素子代
        if child_rel_list:
            for element_child_rel in child_rel_list:
                child = load_element_tree(element_child_rel.CHILD_NO)
                if child:
                    children.append(child)

    else:  # 如果是 SnippetSampler 则读取片段内容
        if 'snippetNo' not in property:
            raise ServiceError('片段编号不能为空')
        snippets = load_element_tree(property['snippetNo'])
        if snippets:
            children.extend(snippets['children'])

    # 类型是Group 或 HTTPSampler 时，查询内置元素并添加至 children 中
    if (
        element.ELEMENT_TYPE == ElementType.GROUP.value  # noqa
        or element.ELEMENT_CLASS == ElementClass.HTTP_SAMPLER.value  # noqa
    ):
        # 查询内置元素关联
        builtin_rel_list = ElementBuiltinChildRelDao.select_all_by_parent(element_no)
        for builtin_rel in builtin_rel_list:
            if builtin_rel.CHILD_TYPE == ElementType.ASSERTION.value:
                # 内置元素为 Assertion 时，添加至第一位（第一个运行 Assertion）
                builtin = load_element_tree(builtin_rel.CHILD_NO)
                if builtin:
                    children.insert(0, builtin)
            else:
                # 其余内置元素添加至最后（最后一个运行）
                builtin = load_element_tree(builtin_rel.CHILD_NO)
                if builtin:
                    children.append(builtin)

    return {
        'name': element.ELEMENT_NAME,
        'remark': element.ELEMENT_REMARK,
        'class': (
            element.ELEMENT_CLASS
            if element.ELEMENT_CLASS != ElementClass.SNIPPET_SAMPLER.value
            else ElementClass.TRANSACTION_CONTROLLER.value
        ),
        'enabled': element.ENABLED,
        'property': property,
        'children': children
    }


def load_element_property(element_no):
    # 查询元素属性，只查询 enabled 的属性
    props = ElementPropertyDao.select_all_by_enable_element(element_no)

    property = {}
    for prop in props:
        if prop.PROPERTY_TYPE == 'STR':
            property[prop.PROPERTY_NAME] = prop.PROPERTY_VALUE
            continue
        if prop.PROPERTY_TYPE == 'DICT':
            property[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
            continue
        if prop.PROPERTY_TYPE == 'LIST':
            property[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
            continue

    return property


def add_flask_socketio_result_collector(script: dict, sid: str):
    log.debug('添加 FlaskSocketIOResultCollector 组件')

    script['children'].insert(
        0, {
            'name': 'FlaskSocketIOResultCollector',
            'remark': '',
            'class': 'FlaskSocketIOResultCollector',
            'enabled': True,
            'property': {
                'FlaskSocketIOResultCollector__namespace': '/',
                'FlaskSocketIOResultCollector__event_name': 'pymeter_result',
                'FlaskSocketIOResultCollector__target_sid': sid,
                'FlaskSocketIOResultCollector__flask_sio_instance_module': 'app.extension',
                'FlaskSocketIOResultCollector__flask_sio_instance_name': 'socketio',
            },
            'children': None
        }
    )


def add_variable_data_set(script: dict, set_no_list, use_current_value):
    log.debug('添加 VariableDataSet 组件')

    variables = get_variables_by_set_list(set_no_list, use_current_value)
    arguments = []
    for name, value in variables.items():
        arguments.append({'class': 'Argument', 'property': {'Argument__name': name, 'Argument__value': value}})

    script['children'].insert(
        0, {
            'name': 'VariableDataSet',
            'remark': '',
            'class': 'VariableDataSet',
            'enabled': True,
            'property': {
                'Arguments__arguments': arguments
            }
        }
    )


def get_variables_by_set_list(set_no_list, use_current_value):
    result = {}
    # 根据列表查询变量集，并根据权重从小到大排序
    set_list = VariableSetDao.select_list_in_set_orderby_weight(*set_no_list)
    if not set_list:
        return result

    for set in set_list:
        # 查询变量列表
        variables = VariableDao.select_list_by_set(set.SET_NO)

        for variable in variables:
            # 过滤非启用状态的变量
            if not variable.ENABLED:
                continue
            if use_current_value and variable.CURRENT_VALUE:
                result[variable.VAR_NAME] = variable.CURRENT_VALUE
            else:
                result[variable.VAR_NAME] = variable.INITIAL_VALUE

    return result


def add_http_header_manager(sampler: TTestElement, children: list):
    log.debug('添加 HTTPHeaderManager 组件')

    # 查询元素关联的请求头模板
    rels = HttpSamplerHeadersRelDao.select_all_by_sampler(sampler.ELEMENT_NO)

    # 没有关联模板时直接跳过
    if not rels:
        return

    # 遍历添加请求头
    property = []
    for rel in rels:
        headers = HttpHeaderDao.select_list_by_template(rel.TEMPLATE_NO)
        for header in headers:
            property.append({
                'class': 'HTTPHeader',
                'property': {
                    'Header__name': header.HEADER_NAME,
                    'Header__value': header.HEADER_VALUE
                }
            })

    # 添加 HTTPHeaderManager 组件
    children.append({
        'name': 'HTTP Header Manager',
        'remark': '',
        'class': 'HTTPHeaderManager',
        'enabled': True,
        'property': {
            'HeaderManager__headers': property
        }
    })


def add_flask_db_result_storage(script: dict, plan_no, report_no, collection_no):
    log.debug('添加 FlaskDBResultStorage 组件')

    script['children'].insert(
        0, {
            'name': 'FlaskDBResultStorage',
            'remark': '',
            'class': 'FlaskDBResultStorage',
            'enabled': True,
            'property': {
                'FlaskDBResultStorage__plan_no': plan_no,
                'FlaskDBResultStorage__report_no': report_no,
                'FlaskDBResultStorage__collection_no': collection_no
            },
            'children': None
        }
    )


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
        collection = load_element_tree(collection_no)
        if not collection:
            log.warn(f'计划编号:[ {plan_no} ] 集合编号:[ {collection_no} ] 脚本为空或脚本已禁用，跳过当前脚本')

        # 添加自定义变量组件
        if set_no_list:
            add_variable_data_set(collection, set_no_list, use_current_value)

        # 添加报告存储器组件
        if report_no:
            add_flask_db_result_storage(collection, plan_no, report_no, collection_no)

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
