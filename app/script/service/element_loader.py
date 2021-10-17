#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_loader.py
# @Time    : 2021-10-02 13:04:49
# @Author  : Kelvin.Ye
from app.common.exceptions import ServiceError
from app.common.validator import check_is_not_blank
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


def loads_tree(element_no, specified_group_no=None, specified_sampler_no=None, self_only=False):
    # 查询元素
    element = TestElementDao.select_by_no(element_no)
    check_is_not_blank(element, '元素不存在')

    # 元素为禁用状态时返回 None
    if not element.ENABLED:
        log.info(f'元素:[ {element.ELEMENT_NAME} ] 已禁用，不需要添加至脚本')
        return None

    # 加载指定元素，如果当前元素非指定元素时返回空
    if specified_group_no or specified_sampler_no:
        if is_not_specified_element(element, specified_group_no, specified_sampler_no, self_only):
            return None

    # 元素子代
    children = []
    # 读取元素属性
    properties = loads_property(element_no)

    # 元素为 HttpSampler 时，添加 HTTP 请求头管理器
    if is_http_sampler(element):
        add_http_header_manager(element, children)

    # 元素为常规 Sampler 时，添加子代
    if not is_snippet_sampler(element):
        children.extend(loads_children(element_no, specified_group_no, specified_sampler_no, self_only))
    # 元素为 SnippetSampler 时，读取片段内容
    else:
        add_snippets(properties, children)
        # SnippetSampler 的属性不需要添加至脚本中
        properties = None

    # 元素为 Group 或 HTTPSampler 时，查询内置元素并添加至 children 中
    if is_group(element) or is_http_sampler(element):
        add_builtin_children(element_no, children)

    return {
        'name': element.ELEMENT_NAME,
        'remark': element.ELEMENT_REMARK,
        'class': (
            element.ELEMENT_CLASS
            if not is_snippet_sampler(element)
            else ElementClass.TRANSACTION_CONTROLLER.value
        ),
        'enabled': element.ENABLED,
        'property': properties,
        'children': children
    }


def loads_property(element_no):
    # 查询元素属性，只查询 enabled 的属性
    props = ElementPropertyDao.select_all_by_enable_element(element_no)

    properties = {}
    for prop in props:
        if prop.PROPERTY_TYPE == 'STR':
            properties[prop.PROPERTY_NAME] = prop.PROPERTY_VALUE
            continue
        if prop.PROPERTY_TYPE == 'DICT':
            properties[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
            continue
        if prop.PROPERTY_TYPE == 'LIST':
            properties[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
            continue

    return properties


def loads_children(element_no, specified_group_no, specified_sampler_no, self_only):
    # 递归查询子代，并根据序号正序排序
    child_rel_list = ElementChildRelDao.select_all_by_parent(element_no)
    children = []
    # 添加子代
    for element_child_rel in child_rel_list:
        child = loads_tree(element_child_rel.CHILD_NO, specified_group_no, specified_sampler_no, self_only)
        if child:
            children.append(child)
    return children


def add_snippets(properties, children: list):
    snippet_no = properties.get('snippetNo', None)
    if not snippet_no:
        raise ServiceError('片段编号不能为空')
    snippets = loads_tree(snippet_no)
    if not snippets:
        return
    transaction = snippets['children']
    add_snippet_config(snippets, transaction, properties.get('arguments', []))
    children.extend(transaction)


def add_builtin_children(element_no, children: list):
    # 查询内置元素关联
    builtin_rel_list = ElementBuiltinChildRelDao.select_all_by_parent(element_no)
    for builtin_rel in builtin_rel_list:
        if builtin_rel.CHILD_TYPE == ElementType.ASSERTION.value:
            # 内置元素为 Assertion 时，添加至第一位（第一个运行 Assertion）
            builtin = loads_tree(builtin_rel.CHILD_NO)
            if builtin:
                children.insert(0, builtin)
        else:
            # 其余内置元素添加至最后（最后一个运行）
            builtin = loads_tree(builtin_rel.CHILD_NO)
            if builtin:
                children.append(builtin)


def add_flask_sio_result_collector(script: dict, sid: str, name: str):
    script['children'].insert(0, {
        'name': 'Dynamic FlaskSIOResultCollector',
        'remark': '',
        'class': 'FlaskSIOResultCollector',
        'enabled': True,
        'property': {
            'FlaskSIOResultCollector__target_sid': sid,
            'FlaskSIOResultCollector__result_name': name,
        }
    })


def add_variable_data_set(script: dict, set_no_list, use_current_value):
    variables = get_variables_by_set_list(set_no_list, use_current_value)
    arguments = []
    for name, value in variables.items():
        arguments.append({'class': 'Argument', 'property': {'Argument__name': name, 'Argument__value': value}})

    script['children'].insert(0, {
        'name': 'Dynamic VariableDataSet',
        'remark': '',
        'class': 'VariableDataSet',
        'enabled': True,
        'property': {
            'Arguments__arguments': arguments
        }
    })


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
        'name': 'Dynamic HTTPHeaderManager',
        'remark': '',
        'class': 'HTTPHeaderManager',
        'enabled': True,
        'property': {
            'HeaderManager__headers': property
        }
    })


def add_flask_db_result_storage(script: dict, plan_no, report_no, collection_no):
    script['children'].insert(0, {
        'name': 'Dynamic FlaskDBResultStorage',
        'remark': '',
        'class': 'FlaskDBResultStorage',
        'enabled': True,
        'property': {
            'FlaskDBResultStorage__plan_no': plan_no,
            'FlaskDBResultStorage__report_no': report_no,
            'FlaskDBResultStorage__collection_no': collection_no
        }
    })


def add_snippet_config(snippet_collection, snippet_children, transaction_parameters):
    snippet_arguments = snippet_collection['property'].get('arguments', [])
    use_http_session = snippet_collection['property'].get('useHTTPSession', 'false')
    if use_http_session == 'true':
        snippet_children.insert(0, {
            'name': 'Dynamic TransactionHTTPSessionManager',
            'remark': '',
            'class': 'TransactionHTTPSessionManager',
            'enabled': True,
            'property': {}
        })

    if transaction_parameters or snippet_arguments:
        arguments = []
        param_dict = {param['name']: param['value'] for param in transaction_parameters}
        for arg in snippet_arguments:
            arguments.append({
                'class': 'Argument',
                'property': {
                    'Argument__name': arg['name'],
                    'Argument__value': param_dict.get(arg['name']) or arg['default']
                }
            })

        snippet_children.insert(0, {
            'name': 'Dynamic TransactionParameter',
            'remark': '',
            'class': 'TransactionParameter',
            'enabled': True,
            'property': {
                'Arguments__arguments': arguments
            }
        })


def is_http_sampler(element):
    return element.ELEMENT_CLASS == ElementClass.HTTP_SAMPLER.value


def is_snippet_sampler(element):
    return element.ELEMENT_CLASS == ElementClass.SNIPPET_SAMPLER.value


def is_test_group(element):
    return element.ELEMENT_CLASS == ElementClass.TEST_GROUP.value


def is_group(element):
    return element.ELEMENT_TYPE == ElementType.GROUP.value


def is_sampler(element):
    return element.ELEMENT_TYPE == ElementType.SAMPLER.value


def is_not_specified_element(element, specified_group_no, specified_sampler_no, self_only):
    """是否非指定的元素

    Args:
        element:                当前元素
        specified_group_no:     指定的 Group 元素编号
        specified_sampler_no:   指定的 Sampler 元素编号
        self_only:              是否仅元素自身

    Returns:

    """
    # 仅元素自身
    if self_only:
        # 非指定 Group
        if is_group(element) and element.ELEMENT_NO != specified_group_no:
            return True
        # 非指定 Sampler
        if not is_group(element) and element.ELEMENT_NO != specified_sampler_no:
            return True
    # 除指定元素外，还需包含配置、控制器、前置、后置和断言
    else:
        # 非指定 TestGroup
        if is_test_group(element) and element.ELEMENT_NO != specified_group_no:
            return True
        # 非指定 Sampler
        if is_sampler(element) and element.ELEMENT_NO != specified_sampler_no:
            return True

    return False
