#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_loader.py
# @Time    : 2021-10-02 13:04:49
# @Author  : Kelvin.Ye
from typing import Dict

from app.common.exceptions import ServiceError
from app.common.validator import check_is_not_blank
from app.script.dao import element_builtin_children_dao as ElementBuiltinChildrenDao
from app.script.dao import element_children_dao as ElementChildrenDao
from app.script.dao import element_property_dao as ElementPropertyDao
from app.script.dao import http_header_dao as HttpHeaderDao
from app.script.dao import http_header_template_ref_dao as HttpHeaderTemplateRefDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.dao import variable_dao as VariableDao
from app.script.dao import variable_dataset_dao as VariableDatasetDao
from app.script.enum import ElementClass
from app.script.enum import ElementType
from app.script.enum import is_debuger
from app.script.enum import is_group
from app.script.enum import is_http_sampler
from app.script.enum import is_sampler
from app.script.enum import is_setup_group_debuger
from app.script.enum import is_snippet_sampler
from app.script.enum import is_teardown_group_debuger
from app.script.model import TTestElement
from app.utils.json_util import from_json
from app.utils.log_util import get_logger


log = get_logger(__name__)


def loads_tree(
        element_no,
        specified_group_no=None,
        specified_sampler_no=None,
        specified_self_only=False,
        no_sampler=False,
        no_debuger=False
):
    """根据元素编号加载脚本"""
    # 查询元素
    element = TestElementDao.select_by_no(element_no)
    check_is_not_blank(element, '元素不存在')

    # 检查是否为运行加载的元素，不允许时直接返回 None
    if is_impassable(element, specified_group_no, specified_self_only, no_sampler, no_debuger):
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
        children.extend(loads_children(element_no, specified_group_no, specified_sampler_no, specified_self_only))
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
        'class': get_real_class(element),
        'enabled': element.ENABLED,
        'property': properties,
        'children': children
    }


def is_impassable(element, specified_group_no, specified_self_only, no_sampler, no_debuger):
    # 元素为禁用状态时返回 None
    if not element.ENABLED:
        log.info(f'元素:[ {element.ELEMENT_NAME} ] 已禁用，不需要添加至脚本')
        return True

    # 加载指定元素，如果当前元素非指定元素时返回空
    if specified_group_no and not is_specified_group(element, specified_group_no, specified_self_only):
        return True

    # 不需要 Sampler 时返回 None
    if no_sampler and is_sampler(element):
        return True

    # 不需要 Debuger 时返回 None
    if no_debuger and is_debuger(element):
        return True

    return False


def get_real_class(element):
    if is_snippet_sampler(element):
        return ElementClass.TRANSACTION_CONTROLLER.value
    elif is_setup_group_debuger(element):
        return ElementClass.SETUP_GROUP_DEBUGER.value
    elif is_teardown_group_debuger(element):
        return ElementClass.TEARDOWN_GROUP_DEBUGER.value
    else:
        return element.ELEMENT_CLASS


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


def loads_children(element_no, specified_group_no, specified_sampler_no, specified_self_only):
    # 递归查询子代，并根据序号正序排序
    children_links = ElementChildrenDao.select_all_by_parent(element_no)
    children = []
    # 添加子代
    for link in children_links:
        found = False
        # 需要指定 Sampler
        if specified_sampler_no:
            # 独立运行
            if specified_self_only:
                if link.CHILD_NO == specified_sampler_no:
                    child = loads_tree(link.CHILD_NO)
                    if child:
                        children.append(child)
            # 非独立运行
            else:
                child = loads_tree(
                    link.CHILD_NO,
                    specified_group_no,
                    specified_sampler_no,
                    specified_self_only,
                    no_sampler=found
                )
                if child:
                    children.append(child)
                if link.CHILD_NO == specified_sampler_no:
                    found = True

        # 无需指定 Sampler
        else:
            child = loads_tree(link.CHILD_NO, specified_group_no, specified_sampler_no, specified_self_only)
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
    builtin_links = ElementBuiltinChildrenDao.select_all_by_parent(element_no)
    for link in builtin_links:
        if link.CHILD_TYPE == ElementType.ASSERTION.value:
            # 内置元素为 Assertion 时，添加至第一位（第一个运行 Assertion）
            builtin = loads_tree(link.CHILD_NO)
            if builtin:
                children.insert(0, builtin)
        else:
            # 其余内置元素添加至最后（最后一个运行）
            builtin = loads_tree(link.CHILD_NO)
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


def add_variable_data_set(script: dict, dataset_number_list, use_current_value, additional: dict = None):
    # 获取变量集
    variables = get_variables_by_dataset_list(dataset_number_list, use_current_value)

    # 添加额外的变量
    if additional:
        for name, value in additional.items():
            # 如果额外变量的值还是变量，则先在变量集中查找真实值并替换
            if value.startswith('${') and value.endswith('}'):
                variables[name] = variables.get(value[2:-1])
            else:
                variables[name] = value

    # 组装为元素
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


def get_variables_by_dataset_list(dataset_number_list, use_current_value) -> Dict:
    result = {}
    # 根据列表查询变量集，并根据权重从小到大排序
    dataset_list = VariableDatasetDao.select_list_in_set_orderby_weight(*dataset_number_list)
    if not dataset_list:
        return result

    for dataset in dataset_list:
        # 查询变量列表
        variables = VariableDao.select_all_by_dataset(dataset.DATASET_NO)

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
    refs = HttpHeaderTemplateRefDao.select_all_by_sampler(sampler.ELEMENT_NO)

    # 没有关联模板时直接跳过
    if not refs:
        return

    # 遍历添加请求头
    property = []
    for ref in refs:
        headers = HttpHeaderDao.select_all_by_template(ref.TEMPLATE_NO)
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


def loads_snippet_collecion(snippets_no, snippets_name, snippets_remark):
    # 读取元素属性
    properties = loads_property(snippets_no)
    use_http_session = properties.get('useHTTPSession', 'false')
    # 递归查询子代，并根据序号正序排序
    children_links = ElementChildrenDao.select_all_by_parent(snippets_no)
    children = []
    # 添加 HTTP Session 组件
    if use_http_session:
        children.append({
            'name': 'Dynamic HTTPSessionManager',
            'remark': '',
            'class': 'HTTPSessionManager',
            'enabled': True,
            'property': {}
        })
    # 添加子代
    for link in children_links:
        child = loads_tree(link.CHILD_NO)
        if child:
            children.append(child)
    # 创建一个临时的 Group
    group = {
        'name': snippets_name,
        'remark': snippets_remark,
        'class': 'TestGroup',
        'enabled': True,
        'property': {
            'TestGroup__on_sample_error': 'start_next_coroutine',
            'TestGroup__number_groups': '1',
            'TestGroup__start_interval': '',
            'TestGroup__main_controller': {
                'class': 'LoopController', 'property': {
                    'LoopController__loops': '1',
                    'LoopController__continue_forever': 'false'
                }
            }
        },
        'children': children
    }
    # 创建一个临时的 Collection
    collection = {
        'name': snippets_name,
        'remark': snippets_remark,
        'class': 'TestCollection',
        'enabled': True,
        'property': {
            'TestCollection__serialize_groups': 'true',
            'TestCollection__delay': '0'
        },
        'children': [group]
    }

    return collection


PASSABLE_ELEMENT_CLASS_LIST = ['SetupGroup', 'TeardownGroup']


def is_specified_group(element, specified_no, self_only):
    # 非 Group 时加载
    if not is_group(element):
        return True  # pass

    # 判断是否为指定的 Group
    if element.ELEMENT_NO == specified_no:
        return True  # pass

    # 非独立运行时，除指定的 Group 外，还需要加载前置和后置 Group）
    if not self_only:
        if element.ELEMENT_CLASS in PASSABLE_ELEMENT_CLASS_LIST:
            return True

    return False
