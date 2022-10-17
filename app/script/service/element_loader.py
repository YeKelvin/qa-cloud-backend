#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_loader.py
# @Time    : 2021-10-02 13:04:49
# @Author  : Kelvin.Ye
from typing import Dict

from app.database import dbquery
from app.script.dao import database_config_dao as DatabaseConfigDao
from app.script.dao import element_children_dao as ElementChildrenDao
from app.script.dao import element_property_dao as ElementPropertyDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.dao import workspace_collection_dao as WorkspaceCollectionDao
from app.script.dao import workspace_component_dao as WorkspaceComponentDao
from app.script.enum import ElementClass
from app.script.enum import ElementType
from app.script.enum import is_debuger
from app.script.enum import is_group
from app.script.enum import is_http_sampler
from app.script.enum import is_sampler
from app.script.enum import is_setup_group_debuger
from app.script.enum import is_snippet_sampler
from app.script.enum import is_sql_sampler
from app.script.enum import is_teardown_group_debuger
from app.script.model import TElementBuiltinChildren
from app.script.service.element_component import add_database_engine
from app.script.service.element_component import add_http_header_manager
from app.tools.exceptions import ServiceError
from app.tools.logger import get_logger
from app.tools.validator import check_exists
from app.utils.json_util import from_json


# from gevent.local import local as CoroutineLocal


log = get_logger(__name__)


def loads_tree(
        element_no,
        specified_group_no=None,
        specified_sampler_no=None,
        specified_selfonly=False,
        no_sampler=False,
        no_debuger=False,
):
    """根据元素编号加载脚本"""
    # 临时缓存
    cache = {}
    # 全局配置临时变量
    config_components = {}
    # 递归加载元素
    script = loads_element(
        element_no,
        specified_group_no=specified_group_no,
        specified_sampler_no=specified_sampler_no,
        specified_selfonly=specified_selfonly,
        no_sampler=no_sampler,
        no_debuger=no_debuger,
        config_components=config_components,
        cache=cache
    )
    if not script:
        raise ServiceError('脚本异常，请重试')
    # 添加全局配置
    # TODO: 空间和全局配置的顺序，后续需要调整
    if config_components:
        for configs in config_components.values():
            for config in configs:
                script['children'].insert(0, config)
    # 添加空间组件（配置器、前置处理器、后置处理器、断言器）
    add_workspace_components(script, element_no)
    return script


def loads_element(
        element_no,
        specified_group_no: str = None,
        specified_sampler_no: str = None,
        specified_selfonly: bool = False,
        no_sampler: bool = False,
        no_debuger: bool = False,
        config_components: Dict[str, list] = None,
        cache: Dict[str, dict] = None
):
    """根据元素编号加载元素数据"""
    # 查询元素
    element = TestElementDao.select_by_no(element_no)
    check_exists(element, error_msg='元素不存在')

    # 检查是否为允许加载的元素，不允许时直接返回 None
    if is_impassable(element, specified_group_no, specified_selfonly, no_sampler, no_debuger):
        return None

    # 元素子代
    children = []
    # 读取元素属性
    properties = loads_property(element_no)

    # 过滤空代码的 Python 组件
    if is_blank_python(element, properties):
        return None

    # 元素为 HttpSampler 时，添加 HTTP 请求头管理器
    if is_http_sampler(element):
        add_http_header_manager(element, children, cache)

    # 元素为 SQLSampler 时，添加全局的数据库引擎配置器
    if is_sql_sampler(element):
        # 查询数据库引擎
        engine = DatabaseConfigDao.select_by_no(properties.get('engineNo'))
        check_exists(engine, error_msg='数据库引擎不存在')
        # 删除引擎编号，PyMeter中不需要
        properties.pop('engineNo')
        # 实时将引擎变量名称写入元素属性中
        properties['SQLSampler__engine_name'] = engine.VARIABLE_NAME
        # 添加数据库引擎配置组件
        add_database_engine(engine, config_components)

    # 元素为 Group 或 HTTPSampler 时，查询内置元素并添加至 children 中
    if is_group(element) or is_http_sampler(element):
        add_builtin_children(element_no, children)

    # 元素为常规 Sampler 时，添加子代
    if not is_snippet_sampler(element):
        children.extend(
            loads_children(
                element_no,
                specified_group_no,
                specified_sampler_no,
                specified_selfonly,
                config_components,
                cache
            )
        )
    # 元素为 SnippetSampler 时，读取片段内容
    else:
        add_snippets(properties, children, config_components, cache)
        properties = None  # SnippetSampler 的属性不需要添加至脚本中

    return {
        'name': element.ELEMENT_NAME,
        'remark': element.ELEMENT_REMARK,
        'class': get_real_class(element),
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


def loads_children(
        element_no,
        specified_group_no,
        specified_sampler_no,
        specified_selfonly,
        config_components: Dict[str, list],
        cache: Dict[str, dict]
):
    """TODO: 太多 if 逻辑，待优化"""
    # 递归查询子代，并根据序号正序排序
    children_relations = ElementChildrenDao.select_all_by_parent(element_no)
    children = []
    # 添加子代
    for relation in children_relations:
        found = False
        # 需要指定 Sampler
        if specified_sampler_no:
            # 独立运行
            if specified_selfonly:
                if relation.CHILD_NO == specified_sampler_no:
                    if child := loads_element(relation.CHILD_NO, config_components=config_components, cache=cache):
                        children.append(child)
            # 非独立运行
            else:
                if child := loads_element(
                    relation.CHILD_NO,
                    specified_group_no,
                    specified_sampler_no,
                    specified_selfonly,
                    no_sampler=found,
                    config_components=config_components,
                    cache=cache
                ):
                    children.append(child)
                if relation.CHILD_NO == specified_sampler_no:  # TODO: 这里有问题
                    found = True
        # 无需指定 Sampler
        else:
            if child := loads_element(
                relation.CHILD_NO,
                specified_group_no,
                specified_sampler_no,
                specified_selfonly,
                config_components=config_components,
                cache=cache
            ):
                children.append(child)

    return children


def add_builtin_children(element_no, children: list):
    # TODO: 排序还是有问题
    relations = (
        dbquery(
            TElementBuiltinChildren.SORT_NUMBER,
            TElementBuiltinChildren.SORT_WEIGHT,
            TElementBuiltinChildren.CHILD_TYPE,
            TElementBuiltinChildren.CHILD_NO
        )
        .filter(
            TElementBuiltinChildren.DELETED == 0,
            TElementBuiltinChildren.PARENT_NO == element_no,
            TElementBuiltinChildren.CHILD_TYPE.in_([
                ElementType.CONFIG.value,
                ElementType.PRE_PROCESSOR.value,
                ElementType.POST_PROCESSOR.value,
                ElementType.ASSERTION.value
            ])
        )
        .order_by(TElementBuiltinChildren.SORT_WEIGHT.desc(), TElementBuiltinChildren.SORT_NUMBER.asc())
        .all()
    )
    for relation in relations:
        log.error(f'{relation=}')
        if builtin := loads_element(relation.CHILD_NO):
            children.append(builtin)


def add_snippets(sampler_property, children: list, config_components: Dict[str, list], cache: Dict[str, dict]):
    snippet_no = sampler_property.get('snippetNo', None)
    if not snippet_no:
        raise ServiceError('片段编号不能为空')
    snippet_collection = loads_element(snippet_no, config_components=config_components, cache=cache)
    if not snippet_collection:
        return
    snippets = snippet_collection['children']
    configure_snippets(snippet_collection, snippets, sampler_property)
    children.extend(snippets)


def add_root_configs(script: dict, config_components: Dict[str, list]):
    for configs in config_components.values():
        for config in configs:
            script['children'].insert(0, config)


def configure_snippets(snippet_collection, snippet_children, sampler_property):
    # SnippetCollection 属性
    snippet_parameters = snippet_collection['property'].get('parameters', [])
    use_http_session = snippet_collection['property'].get('useHTTPSession', 'false')

    # SnippetSampler 属性
    sampler_arguments = sampler_property.get('arguments', [])
    use_default = sampler_property.get('useDefault', 'false') == 'true'

    # 添加 TransactionHTTPSessionManager 组件
    if use_http_session == 'true':
        snippet_children.insert(0, {
            'name': 'Transaction HTTP SessionManager',
            'remark': '',
            'class': 'TransactionHTTPSessionManager',
            'enabled': True,
            'property': {}
        })

    if sampler_arguments or snippet_parameters:
        arguments = []
        if use_default:  # 使用片段集合的默认值
            for param in snippet_parameters:
                arguments.append({
                    'class': 'Argument',
                    'property': {
                        'Argument__name': param['name'],
                        'Argument__value': param['default']
                    }
                })
        else:  # 使用自定义的参数值
            args = {arg['name']: arg['value'] for arg in sampler_arguments}
            for param in snippet_parameters:
                arguments.append({
                    'class': 'Argument',
                    'property': {
                        'Argument__name': param['name'],
                        'Argument__value': args.get(param['name']) or param['default']
                    }
                })

        # 添加 TransactionParameter 组件
        snippet_children.insert(0, {
            'name': 'Transaction Parameter',
            'remark': '',
            'class': 'TransactionParameter',
            'enabled': True,
            'property': {
                'Arguments__arguments': arguments
            }
        })


def loads_snippet_collecion(snippet_no, snippet_name, snippet_remark):
    # 缓存
    cache = {}
    # 读取元素属性
    properties = loads_property(snippet_no)
    use_http_session = properties.get('useHTTPSession', 'false')
    # 递归查询子代，并根据序号正序排序
    children_relations = ElementChildrenDao.select_all_by_parent(snippet_no)
    children = []
    # 添加 HTTP Session 组件
    if use_http_session:
        children.append({
            'name': 'HTTP Session Manager',
            'remark': '',
            'class': 'HTTPSessionManager',
            'enabled': True,
            'property': {}
        })
    # 添加子代
    for relation in children_relations:
        if child := loads_element(relation.CHILD_NO, cache=cache):
            children.append(child)
    # 创建一个临时的 Group
    group = {
        'name': snippet_name,
        'remark': snippet_remark,
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
    return {
        'name': snippet_name,
        'remark': snippet_remark,
        'class': 'TestCollection',
        'enabled': True,
        'property': {
            'TestCollection__serialize_groups': 'true',
            'TestCollection__delay': '0'
        },
        'children': [group]
    }


def add_workspace_components(script: dict, element_no: str):
    collection_no = get_root_no(element_no)
    workspace_no = get_workspace_no(collection_no)
    workspace_components = WorkspaceComponentDao.select_all_by_workspace(workspace_no)
    if not workspace_components:
        return
    components = []
    for workspace_component in workspace_components:
        if element := loads_element(workspace_component.COMPONENT_NO):
            components.append(element)
    for component in components[::-1]:
        script['children'].insert(0, component)


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


def is_blank_python(element, properties):
    if (
            element.ELEMENT_CLASS == ElementClass.PYTHON_PRE_PROCESSOR.value and
            not properties.get('PythonPreProcessor__script').strip()
    ):
        return True
    if (
            element.ELEMENT_CLASS == ElementClass.PYTHON_POST_PROCESSOR.value and
            not properties.get('PythonPostProcessor__script').strip()
    ):
        return True
    if (
            element.ELEMENT_CLASS == ElementClass.PYTHON_ASSERTION.value and
            not properties.get('PythonAssertion__script').strip()
    ):
        return True
    return False


def is_impassable(element, specified_group_no, specified_selfonly, no_sampler, no_debuger):
    # 元素为禁用状态时返回 None
    if not element.ENABLED:
        log.info(f'元素:[ {element.ELEMENT_NAME} ] 已禁用，不需要添加至脚本')
        return True

    # 加载指定元素，如果当前元素非指定元素时返回空
    if specified_group_no and not is_specified_group(element, specified_group_no, specified_selfonly):
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


def get_root_no(element_no):
    """根据元素编号获取根元素编号（集合编号）"""
    if not (element_child := ElementChildrenDao.select_by_child(element_no)):
        return element_no
    if not element_child.ROOT_NO:
        raise ServiceError(f'元素编号:[ {element_no} ] 根元素编号为空')
    return element_child.ROOT_NO


def get_workspace_no(collection_no) -> str:
    """获取元素空间编号"""
    if workspace_collection := WorkspaceCollectionDao.select_by_collection(collection_no):
        return workspace_collection.WORKSPACE_NO
    else:
        raise ServiceError('查询元素空间失败')
