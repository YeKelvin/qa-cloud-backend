#!/usr/bin/ python3
# @File    : element_loader.py
# @Time    : 2021-10-02 13:04:49
# @Author  : Kelvin.Ye
from typing import Dict

from loguru import logger

from app.database import dbquery
from app.modules.script.dao import element_children_dao
from app.modules.script.dao import element_property_dao
from app.modules.script.dao import test_element_dao
from app.modules.script.dao import workspace_component_dao
from app.modules.script.dao import workspace_settings_dao
from app.modules.script.enum import ElementClass
from app.modules.script.enum import ElementType
from app.modules.script.enum import is_debuger
from app.modules.script.enum import is_http_sampler
from app.modules.script.enum import is_python_assertion
from app.modules.script.enum import is_python_post_processor
from app.modules.script.enum import is_python_prev_processor
from app.modules.script.enum import is_setup_debuger
from app.modules.script.enum import is_snippet_sampler
from app.modules.script.enum import is_sql_sampler
from app.modules.script.enum import is_teardown_debuger
from app.modules.script.enum import is_test_collection
from app.modules.script.enum import is_test_worker
from app.modules.script.enum import is_worker
from app.modules.script.manager.element_component import add_database_engine
from app.modules.script.manager.element_component import add_http_header_manager
from app.modules.script.manager.element_component import add_http_session_manager
from app.modules.script.manager.element_component import create_test_collection
from app.modules.script.manager.element_component import create_test_worker
from app.modules.script.manager.element_context import loads_cache
from app.modules.script.manager.element_context import loads_configurator
from app.modules.script.manager.element_manager import get_workspace_no
from app.modules.script.model import TElementComponents
from app.tools.exceptions import ServiceError
from app.tools.validator import check_exists
from app.utils.json_util import from_json


def loads_tree(
        collection_no,
        specify_worker_no=None,
        specify_sampler_no=None,
        exclude_debuger=False,
):
    """根据元素编号加载脚本"""
    logger.debug(
        f'开始从数据库中加载脚本, '
        f'指定的工作者编号:[ {specify_worker_no} ], '
        f'指定的取样器编号:[ {specify_sampler_no} ], '
        f'排除调试器:[ {exclude_debuger} ]'
    )
    # 配置上下文变量，用于临时缓存
    cache_token = loads_cache.set({})
    configurator_token = loads_configurator.set({})
    # 递归加载元素
    collection = loads_element(collection_no, specify_worker_no, specify_sampler_no, exclude_debuger)
    if not collection:
        raise ServiceError('脚本异常，请联系管理员')
    # 添加全局配置
    for configs in loads_configurator.get().values():
        for config in configs:
            collection['children'].insert(0, config)
    collection_properties = collection.get('property')
    collection_attributes = collection.get('attributes')
    exclude_workspaces = collection_attributes.get('exclude_workspaces', False)
    # 添加空间组件（配置器、前置处理器、后置处理器、测试断言器）
    if not exclude_workspaces:
        workspace_no = get_workspace_no(collection_no)
        # 加载空间组件
        components = loads_workspace_components(workspace_no)
        # 添加至脚本头部
        for component in components[::-1]:
            collection['children'].insert(0, component)
        # 合并空间和集合的运行策略
        merge_workspace_settings_to_collection(workspace_no, collection_properties)
    # 清空上下文变量
    loads_cache.reset(cache_token)
    loads_configurator.reset(configurator_token)
    return collection


def loads_element(
        element_no,
        specify_worker_no: str = None,
        specify_sampler_no: str = None,
        exclude_debuger: bool = False
):
    """根据元素编号加载元素数据"""
    # 查询元素
    element = test_element_dao.select_by_no(element_no)
    check_exists(element, error_msg='元素不存在')

    # 元素为禁用状态时返回 None
    if not element.ENABLED:
        logger.debug(f'元素名称:[ {element.ELEMENT_NAME} ] 元素已禁用, 无需加载')
        return None

    # 排除 debuger
    if  exclude_debuger and is_debuger(element):
        logger.debug(f'元素名称:[ {element.ELEMENT_NAME} ] 元素为调试器, 无需加载')
        return None

    # 加载指定的 ，如果当前元素非指定的worker时返回 None
    if specify_worker_no and is_test_worker(element) and element.ELEMENT_NO != specify_worker_no:
        logger.debug(f'元素名称:[ {element.ELEMENT_NAME} ] 元素为非指定的工作者, 无需加载')
        return None

    # 元素子代
    children = []
    # 元素属性
    properties = loads_property(element_no)
    attributes = element.ELEMENT_ATTRIBUTES or {}

    # 添加HTTP会话管理器
    if is_worker(element) and attributes.get('enable_http_session', False):
        add_http_session_manager(attributes.get('clear_http_session_for_each_iteration', False), children)

    # 过滤空代码的 Python 组件
    if is_blank_python(element, properties):
        logger.debug(f'元素名称:[ {element.ELEMENT_NAME} ] 元素中的Python代码为空, 无需加载')
        return None

    # 添加HTTP请求头管理器
    if is_http_sampler(element):
        add_http_header_manager(element, children)

    # 添加数据库引擎配置器
    if is_sql_sampler(element):
        add_database_engine(attributes.get('engine_no'), properties)

    # 添加元素组件
    if is_test_collection(element) or is_worker(element) or is_http_sampler(element):
        add_element_components(element_no, children)

    # 非片段请求时直接添加子代
    if not is_snippet_sampler(element):
        children.extend(
            loads_children(element_no, specify_worker_no, specify_sampler_no)
        )
    # 片段请求则查询片段内容
    else:
        add_snippets(attributes, children)

    return {
        'name': element.ELEMENT_NAME,
        'remark': element.ELEMENT_REMARK,
        'class': get_real_class(element),
        'enabled': element.ENABLED,
        'attributes': attributes,
        'property': properties,
        'children': children
    }


def loads_property(element_no):
    # 查询元素属性，只查询 enabled 的属性
    props = element_property_dao.select_all_by_enable_element(element_no)

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


def loads_children(element_no, specify_worker_no, specify_sampler_no):
    # TODO: 优化查询sql，查children时连表查询children和element
    # 查询子代，并根据序号正序排序
    relations = element_children_dao.select_all_by_parent(element_no)
    children = []
    # 添加子代
    for relation in relations:
        # 加载子代元素
        if child := loads_element(relation.CHILD_NO, specify_worker_no, specify_sampler_no):
            children.append(child)
        # 找到指定的 Sampler 就返回
        if specify_sampler_no and relation.CHILD_NO == specify_sampler_no:
            return children

    return children


def add_element_components(element_no, children: list):
    # TODO: 排序还是有问题
    relations = (
        dbquery(
            TElementComponents.SORT_NUMBER,
            TElementComponents.SORT_WEIGHT,
            TElementComponents.CHILD_TYPE,
            TElementComponents.CHILD_NO
        )
        .filter(
            TElementComponents.DELETED == 0,
            TElementComponents.PARENT_NO == element_no,
            TElementComponents.CHILD_TYPE.in_([
                ElementType.CONFIG.value,
                ElementType.PREV_PROCESSOR.value,
                ElementType.POST_PROCESSOR.value,
                ElementType.ASSERTION.value
            ])
        )
        .order_by(TElementComponents.SORT_WEIGHT.desc(), TElementComponents.SORT_NUMBER.asc())
        .all()
    )
    for relation in relations:
        if component := loads_element(relation.CHILD_NO):
            children.append(component)


def add_snippets(sampler_attrs, children: list):
    # 根据片段编号加载片段集合（片段集合在脚本中其实是事务，这里做了一层转换）
    snippet_no = sampler_attrs.get('snippet_no', None)
    if not snippet_no:
        raise ServiceError('片段编号不能为空')
    # 加载片段集合
    transaction = loads_element(snippet_no)
    if not transaction:
        return
    transaction_children = transaction.get('children')
    if not transaction_children:
        return
    trans_attrs = transaction.get('attributes', {})
    # 片段形参
    parameters = trans_attrs.get('parameters', [])
    # 是否使用HTTP会话
    use_http_session = trans_attrs.get('use_http_session', False)
    # 片段实参
    arguments = sampler_attrs.get('arguments', [])
    # 是否使用形参默认值
    use_default = sampler_attrs.get('use_default', False)
    # 配置片段
    configure_snippets(transaction_children, parameters, arguments, use_http_session, use_default)
    children.extend(transaction_children)


def add_root_configs(script: dict, config_components: Dict[str, list]):
    for configs in config_components.values():
        for config in configs:
            script['children'].insert(0, config)


def configure_snippets(children: list, parameters: list, arguments: list, use_http_session: bool, use_default: bool):
    # 添加 TransactionHTTPSessionManager 组件
    if use_http_session:
        children.insert(0, {
            'name': '事务HTTP会话管理器',
            'remark': '',
            'class': 'TransactionHTTPSessionManager',
            'enabled': True,
            'property': {}
        })

    if arguments or parameters:
        arguments = []
        if use_default:  # 使用片段集合的默认值
            arguments.extend(
                {
                    'class': 'Argument',
                    'property': {
                        'Argument__name': param['name'],
                        'Argument__value': param['default'],
                    },
                }
                for param in parameters
            )
        else:  # 使用自定义的参数值
            args = {arg['name']: arg['value'] for arg in arguments}
            arguments.extend(
                {
                    'class': 'Argument',
                    'property': {
                        'Argument__name': param['name'],
                        'Argument__value': args.get(param['name'])
                        or param['default'],
                    },
                }
                for param in parameters
            )
        # 添加 TransactionParameter 组件
        children.insert(0, {
            'name': '事务参数',
            'remark': '',
            'class': 'TransactionParameter',
            'enabled': True,
            'property': {
                'Arguments__arguments': arguments
            }
        })


def loads_snippet_collecion(snippet_no, snippet_name, snippet_remark):
    # 配置上下文变量，用于临时缓存
    cache_token = loads_cache.set({})
    # 查询元素
    element = test_element_dao.select_by_no(snippet_no)
    check_exists(element, error_msg='元素不存在')
    attributes = element.ELEMENT_ATTRIBUTES or {}
    use_http_session = attributes.get('use_http_session', False)
    # 递归查询子代，并根据序号正序排序
    lower_relation_list = element_children_dao.select_all_by_parent(snippet_no)
    children = []
    # 添加 HTTP Session 组件
    if use_http_session:
        children.append({
            'name': 'HTTP会话管理器',
            'remark': '',
            'class': 'HTTPSessionManager',
            'enabled': True,
            'property': {}
        })
    # 添加子代
    for relation in lower_relation_list:
        if child := loads_element(relation.CHILD_NO):
            children.append(child)
    # 清空上下文变量
    loads_cache.reset(cache_token)
    # 创建一个临时的 Worker
    worker = create_test_worker(name=snippet_name, children=children)
    # 创建一个临时的 Collection
    return create_test_collection(name=snippet_name, remark=snippet_remark, children=[worker])


def loads_workspace_components(workspace_no):
    workspace_components = workspace_component_dao.select_all_by_workspace(workspace_no)
    if not workspace_components:
        return []

    components = []
    for workspace_component in workspace_components:
        if element := loads_element(workspace_component.COMPONENT_NO):
            element['level'] = 0  # 给空间组件添加层级
            components.append(element)
    return components


def is_specified_worker(element, worker_no):
    return is_test_worker(element) and element.ELEMENT_NO == worker_no


def is_blank_python(element, properties):
    if is_python_prev_processor(element) and not properties.get('PythonPrevProcessor__script').strip():
        return True
    if is_python_post_processor(element) and not properties.get('PythonPostProcessor__script').strip():
        return True
    return is_python_assertion(element) and not properties.get('PythonAssertion__script').strip()


def get_real_class(element):
    if is_snippet_sampler(element):
        return ElementClass.TRANSACTION_CONTROLLER.value
    elif is_setup_debuger(element):
        return ElementClass.SETUP_DEBUGER.value
    elif is_teardown_debuger(element):
        return ElementClass.TEARDOWN_DEBUGER.value
    else:
        return element.ELEMENT_CLASS


def merge_workspace_settings_to_collection(workspace_no, collection_properties):
    # 查询集合运行策略
    collection_running_strategy = collection_properties.get('TestCollection__running_strategy', {})
    # 优先使用集合的运行策略
    if collection_running_strategy.get('reverse', []):
        return
    # 查询空间设置
    workspace_settings = workspace_settings_dao.select_by_workspace(workspace_no)
    if not workspace_settings:
        return
    # 集合的运行策略没有设置时，合并空间的运行策略
    workspace_running_strategy = workspace_settings.DATA.get('running_strategy', {})
    if workspace_run_reverse := workspace_running_strategy.get('reverse', []):
        collection_running_strategy['reverse'] = workspace_run_reverse
        collection_properties['TestCollection__running_strategy'] = collection_running_strategy
    else:
        return
