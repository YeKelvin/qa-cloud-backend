#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_service.py
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
import traceback

from pymeter.runner import Runner

from app.common.decorators.service import http_service
from app.common.exceptions import ServiceError
from app.common.validator import check_is_not_blank
from app.extension import executor
from app.extension import socketio
from app.script.dao import element_builtin_child_rel_dao as ElementBuiltinChildRelDao
from app.script.dao import element_child_rel_dao as ElementChildRelDao
from app.script.dao import element_property_dao as ElementPropertyDao
from app.script.dao import http_header_dao as HttpHeaderDao
from app.script.dao import http_sampler_headers_rel_dao as HttpSamplerHeadersRelDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.dao import variable_dao as VariableDao
from app.script.dao import variable_set_dao as VariableSetDao
from app.script.enum import ElementClass
from app.script.enum import ElementType
from app.script.model import TTestElement
from app.utils.json_util import from_json
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def execute_script(req):
    # 根据 collectionNo 递归查询脚本数据并转换成 dict
    collection = load_element_tree(req.collectionNo)

    # TODO: 增加脚本完整性校验，例如脚本下是否有内容

    if req.sid:
        add_flask_socketio_result_collector(collection, req.sid)

    if req.variableSet:
        add_variable_data_set(collection, req.variableSet)

    script = [collection]

    # 新开一个线程执行脚本
    def start():
        sid = req.sid
        try:
            Runner.start(script, throw_ex=True)
        except Exception:
            log.error(traceback.format_exc())
            socketio.emit('pymeter_error', '脚本执行异常，请联系管理员', namespace='/', to=sid)

    # TODO: 暂时用ThreadPoolExecutor，后面改用Celery，https://www.celerycn.io/
    executor.submit(start)


def load_element_tree(element_no):
    # 查询元素
    element = TestElementDao.select_by_no(element_no)
    check_is_not_blank(element, '元素不存在')

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
                children.append(load_element_tree(element_child_rel.CHILD_NO))

    else:  # 如果是 SnippetSampler 则读取片段内容
        if 'snippetNo' not in property:
            raise ServiceError('片段编号不能为空')
        children.extend(load_element_tree(property['snippetNo'])['children'])

    # 如果元素为 HTTPSampler 时，查询内置元素并添加至 children 中
    if (
        element.ELEMENT_TYPE == ElementType.GROUP.value  # noqa
        or element.ELEMENT_CLASS == ElementClass.HTTP_SAMPLER.value  # noqa
    ):
        # 查询内置元素关联
        builtin_rel_list = ElementBuiltinChildRelDao.select_all_by_parent(element_no)
        for builtin_rel in builtin_rel_list:
            if builtin_rel.CHILD_TYPE == ElementType.ASSERTION.value:
                # 内置元素为 Assertion 时，添加至第一位（第一个运行 Assertion）
                children.insert(0, load_element_tree(builtin_rel.CHILD_NO))
            else:
                # 其余内置元素添加至最后（最后一个运行）
                children.append(load_element_tree(builtin_rel.CHILD_NO))

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
            'remark': None,
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


def add_variable_data_set(script: dict, variable_set):
    log.debug('添加 VariableDataSet 组件')

    variables = get_variables_by_set_list(variable_set.list, variable_set.useCurrentValue)
    arguments = []
    for name, value in variables.items():
        arguments.append({'class': 'Argument', 'property': {'Argument__name': name, 'Argument__value': value}})

    script['children'].insert(
        0, {
            'name': '变量配置器',
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
