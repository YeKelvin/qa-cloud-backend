#!/usr/bin/ python3
# @File    : element_loader.py
# @Time    : 2021-10-02 13:04:49
# @Author  : Kelvin.Ye
from typing import Dict

from app.database import dbquery
from app.modules.script.dao import database_config_dao
from app.modules.script.dao import element_children_dao
from app.modules.script.dao import element_property_dao
from app.modules.script.dao import test_element_dao
from app.modules.script.dao import workspace_component_dao
from app.modules.script.enum import ElementClass
from app.modules.script.enum import ElementType
from app.modules.script.enum import is_debuger
from app.modules.script.enum import is_http_sampler
from app.modules.script.enum import is_python_assertion
from app.modules.script.enum import is_python_post_processor
from app.modules.script.enum import is_python_pre_processor
from app.modules.script.enum import is_setup_debuger
from app.modules.script.enum import is_snippet_sampler
from app.modules.script.enum import is_sql_sampler
from app.modules.script.enum import is_teardown_debuger
from app.modules.script.enum import is_test_collection
from app.modules.script.enum import is_test_worker
from app.modules.script.enum import is_worker
from app.modules.script.manager.element_component import add_database_engine
from app.modules.script.manager.element_component import add_http_header_manager
from app.modules.script.manager.element_context import loads_cache
from app.modules.script.manager.element_context import loads_configurator
from app.modules.script.manager.element_manager import get_root_no
from app.modules.script.manager.element_manager import get_workspace_no
from app.modules.script.model import TElementComponents
from app.tools.exceptions import ServiceError
from app.tools.validator import check_exists
from app.utils.json_util import from_json


def loads_tree(
        element_no,
        specify_worker_no=None,
        specify_sampler_no=None,
        exclude_debuger=False,
):
    """根据元素编号加载脚本"""
    # 配置上下文变量，用于临时缓存
    cache_token = loads_cache.set({})
    configurator_token = loads_configurator.set({})
    # 递归加载元素
    script = loads_element(element_no, specify_worker_no, specify_sampler_no, exclude_debuger)
    if not script:
        raise ServiceError('脚本异常，请重试')
    # 添加全局配置
    for configs in loads_configurator.get().values():
        for config in configs:
            script['children'].insert(0, config)
    # 查询集合配置
    collection = test_element_dao.select_by_no(element_no)
    collection_attributes = collection.ELEMENT_ATTRIBUTES
    exclude_workspaces = collection_attributes.get('exclude_workspaces', False)
    # 添加空间组件（配置器、前置处理器、后置处理器、断言器）
    if not exclude_workspaces:
        components = loads_workspace_components(element_no)
        for component in components[::-1]:
            script['children'].insert(0, component)
    # 清空上下文变量
    loads_cache.reset(cache_token)
    loads_configurator.reset(configurator_token)
    return script


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
        return None

    # 排除 debuger
    if  exclude_debuger and is_debuger(element):
        return None

    # 加载指定的 ，如果当前元素非指定的worker时返回 None
    if specify_worker_no and is_test_worker(element) and element.ELEMENT_NO != specify_worker_no:
        return None

    # 元素子代
    children = []
    # 元素属性
    properties = loads_property(element_no)

    # 过滤空代码的 Python 组件
    if is_blank_python(element, properties):
        return None

    # 元素为 HttpSampler 时，添加 HTTP 请求头管理器
    if is_http_sampler(element):
        add_http_header_manager(element, children)

    # 元素为 SQLSampler 时，添加全局的数据库引擎配置器
    if is_sql_sampler(element):
        # 查询数据库引擎
        engine = database_config_dao.select_by_no(properties.get('engineNo'))
        check_exists(engine, error_msg='数据库引擎不存在')
        # 删除引擎编号，PyMeter中不需要
        properties.pop('engineNo')
        # 实时将引擎变量名称写入元素属性中
        properties['SQLSampler__engine_name'] = engine.VARIABLE_NAME
        # 添加数据库引擎配置组件
        add_database_engine(engine)

    # 添加元素组件
    if is_test_collection(element) or is_worker(element) or is_http_sampler(element):
        add_element_components(element_no, children)

    # 元素为非 SnippetSampler 时，添加子代
    if not is_snippet_sampler(element):
        children.extend(
            loads_children(element_no, specify_worker_no, specify_sampler_no)
        )
    # 元素为 SnippetSampler 时，查询片段内容
    else:
        add_snippets(properties, children)
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
                ElementType.PRE_PROCESSOR.value,
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


def add_snippets(sampler_property, children: list):
    snippet_no = sampler_property.get('snippetNo', None)
    if not snippet_no:
        raise ServiceError('片段编号不能为空')
    snippet_collection = loads_element(snippet_no)
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
            'name': '事务HTTP会话管理器',
            'remark': '',
            'class': 'TransactionHTTPSessionManager',
            'enabled': True,
            'property': {}
        })

    if sampler_arguments or snippet_parameters:
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
                for param in snippet_parameters
            )
        else:  # 使用自定义的参数值
            args = {arg['name']: arg['value'] for arg in sampler_arguments}
            arguments.extend(
                {
                    'class': 'Argument',
                    'property': {
                        'Argument__name': param['name'],
                        'Argument__value': args.get(param['name'])
                        or param['default'],
                    },
                }
                for param in snippet_parameters
            )
        # 添加 TransactionParameter 组件
        snippet_children.insert(0, {
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
    # 读取元素属性
    properties = loads_property(snippet_no)
    use_http_session = properties.get('useHTTPSession', 'false')
    # 递归查询子代，并根据序号正序排序
    children_relations = element_children_dao.select_all_by_parent(snippet_no)
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
    for relation in children_relations:
        if child := loads_element(relation.CHILD_NO):
            children.append(child)
    # 清空上下文变量
    loads_cache.reset(cache_token)
    # 创建一个临时的 Worker
    worker = {
        'name': snippet_name,
        'remark': '',
        'class': 'TestWorker',
        'enabled': True,
        'property': {
            'TestWorker__on_sample_error': 'start_next_thread',
            'TestWorker__number_of_threads': '1',
            'TestWorker__start_interval': '',
            'TestWorker__main_controller': {
                'class': 'LoopController',
                'property': {
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
            'TestCollection__serialize_workers': 'true',
            'TestCollection__delay': '0'
        },
        'children': [worker]
    }


def loads_workspace_components(element_no):
    collection_no = get_root_no(element_no)
    workspace_no = get_workspace_no(collection_no)
    workspace_components = workspace_component_dao.select_all_by_workspace(workspace_no)
    if not workspace_components:
        return
    components = []
    for workspace_component in workspace_components:
        if element := loads_element(workspace_component.COMPONENT_NO):
            element['level'] = 0  # 给空间组件添加层级
            components.append(element)
    return components


def is_specified_worker(element, worker_no):
    return is_test_worker(element) and element.ELEMENT_NO == worker_no


def is_blank_python(element, properties):
    if is_python_pre_processor(element) and not properties.get('PythonPreProcessor__script').strip():
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
