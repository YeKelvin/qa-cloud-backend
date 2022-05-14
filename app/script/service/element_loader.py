#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_loader.py
# @Time    : 2021-10-02 13:04:49
# @Author  : Kelvin.Ye
from typing import Dict

from app.common.exceptions import ServiceError
from app.common.validator import check_exists
from app.script.dao import database_config_dao as DatabaseConfigDao
from app.script.dao import element_builtin_children_dao as ElementBuiltinChildrenDao
from app.script.dao import element_children_dao as ElementChildrenDao
from app.script.dao import element_property_dao as ElementPropertyDao
from app.script.dao import http_header_dao as HttpHeaderDao
from app.script.dao import http_header_template_ref_dao as HttpHeaderTemplateRefDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.dao import variable_dao as VariableDao
from app.script.dao import variable_dataset_dao as VariableDatasetDao
from app.script.enum import DatabaseDriver
from app.script.enum import DatabaseType
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
from app.script.model import TTestElement
from app.utils.json_util import from_json
from app.utils.log_util import get_logger


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
    if config_components:
        for configs in config_components.values():
            for config in configs:
                script['children'].insert(0, config)

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
    check_exists(element, '元素不存在')

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
        check_exists(engine, '数据库引擎不存在')
        # 删除引擎编号，PyMeter中不需要
        properties.pop('engineNo')
        # 实时将引擎变量名称写入元素属性中
        properties['SQLSampler__engine_name'] = engine.VARIABLE_NAME
        # 添加数据库引擎配置组件
        add_database_engine(engine, config_components)

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
    # 递归查询子代，并根据序号正序排序
    children_links = ElementChildrenDao.select_all_by_parent(element_no)
    children = []
    # 添加子代
    for link in children_links:
        found = False
        # 需要指定 Sampler
        if specified_sampler_no:
            # 独立运行
            if specified_selfonly:
                if link.CHILD_NO == specified_sampler_no:
                    if child := loads_element(link.CHILD_NO, config_components=config_components, cache=cache):
                        children.append(child)
            # 非独立运行
            else:
                if child := loads_element(
                    link.CHILD_NO,
                    specified_group_no,
                    specified_sampler_no,
                    specified_selfonly,
                    no_sampler=found,
                    config_components=config_components,
                    cache=cache
                ):
                    children.append(child)
                if link.CHILD_NO == specified_sampler_no:  # TODO: 这里有问题
                    found = True
        # 无需指定 Sampler
        else:
            if child := loads_element(
                link.CHILD_NO,
                specified_group_no,
                specified_sampler_no,
                specified_selfonly,
                config_components=config_components,
                cache=cache
            ):
                children.append(child)

    return children


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


def add_builtin_children(element_no, children: list):
    # 查询内置元素关联
    builtin_links = ElementBuiltinChildrenDao.select_all_by_parent(element_no)
    for link in builtin_links:
        if link.CHILD_TYPE == ElementType.ASSERTION.value:
            # 内置元素为 Assertion 时，添加至第一位（第一个运行 Assertion）
            if builtin := loads_element(link.CHILD_NO):
                children.insert(0, builtin)
        else:
            # 其余内置元素添加至最后（最后一个运行）
            if builtin := loads_element(link.CHILD_NO):
                children.append(builtin)


def add_flask_sio_result_collector(script: dict, sid: str, result_id: str, result_name: str):
    # 添加 FlaskSIOResultCollector 组件
    script['children'].insert(0, {
        'name': 'FlaskSIOResultCollector',
        'remark': '',
        'class': 'FlaskSIOResultCollector',
        'enabled': True,
        'property': {
            'FlaskSIOResultCollector__target_sid': sid,
            'FlaskSIOResultCollector__result_id': result_id,
            'FlaskSIOResultCollector__result_name': result_name,
        }
    })


def add_variable_dataset(script: dict, dataset_number_list: list, use_current_value: bool, additional: dict = None):
    # 不存在变量集就忽略了
    if not dataset_number_list:
        return

    # 获取变量集
    variables = get_variables_by_datasets(dataset_number_list, use_current_value)

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
        arguments.append({
            'class': 'Argument',
            'property': {
                'Argument__name': name,
                'Argument__value': value
            }
        })

    # 添加 VariableDataset 组件
    script['children'].insert(0, {
        'name': 'VariableDataset',
        'remark': '',
        'class': 'VariableDataset',
        'enabled': True,
        'property': {
            'Arguments__arguments': arguments
        }
    })


def get_variables_by_datasets(dataset_number_list: list, use_current_value: bool) -> Dict:
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


def add_http_header_manager(sampler: TTestElement, children: list, cache: Dict[str, dict]):
    # 查询元素关联的请求头模板
    refs = HttpHeaderTemplateRefDao.select_all_by_sampler(sampler.ELEMENT_NO)

    # 没有关联模板时直接跳过
    if not refs:
        return

    # 获取请求头管理器缓存
    header_manager_cache = cache.get(ElementClass.HTTP_HEADER_MANAGER.value, {})
    if not header_manager_cache:
        cache[ElementClass.HTTP_HEADER_MANAGER.value] = header_manager_cache

    # 遍历添加请求头
    properties = []
    for ref in refs:
        # 先查缓存
        headers_cache = header_manager_cache.get(ref.TEMPLATE_NO, [])
        if not headers_cache:
            headers = HttpHeaderDao.select_all_by_template(ref.TEMPLATE_NO)
            for header in headers:
                headers_cache.append({
                    'class': 'HTTPHeader',
                    'property': {
                        'Header__name': header.HEADER_NAME,
                        'Header__value': header.HEADER_VALUE
                    }
                })
            header_manager_cache[ref.TEMPLATE_NO] = headers_cache
        properties.extend(headers_cache)

    # 添加 HTTPHeaderManager 组件
    children.append({
        'name': 'HTTPHeaderManager',
        'remark': '',
        'class': 'HTTPHeaderManager',
        'enabled': True,
        'property': {
            'HeaderManager__headers': properties
        }
    })


def add_flask_db_result_storage(script: dict, report_no, collection_no):
    # 添加 FlaskDBResultStorage 组件
    script['children'].insert(0, {
        'name': 'FlaskDBResultStorage',
        'remark': '',
        'class': 'FlaskDBResultStorage',
        'enabled': True,
        'property': {
            'FlaskDBResultStorage__report_no': report_no,
            'FlaskDBResultStorage__collection_no': collection_no
        }
    })


def add_flask_db_iteration_storage(script: dict, execution_no, collection_no):
    # 添加 FlaskDBIterationStorage 组件
    script['children'].insert(0, {
        'name': 'FlaskDBIterationStorage',
        'remark': '',
        'class': 'FlaskDBIterationStorage',
        'enabled': True,
        'property': {
            'FlaskDBIterationStorage__execution_no': execution_no,
            'FlaskDBIterationStorage__collection_no': collection_no
        }
    })


def add_root_configs(script: dict, config_components: Dict[str, list]):
    for configs in config_components.values():
        for config in configs:
            script['children'].insert(0, config)


def add_database_engine(engine, config_components: dict):
    engines = config_components.get(ElementClass.DATABASE_ENGINE.value, [])
    if not engines:
        config_components[ElementClass.DATABASE_ENGINE.value] = engines
    engines.append({
        'name': engine.CONFIG_NAME,
        'remark': engine.CONFIG_DESC,
        'class': 'DatabaseEngine',
        'enabled': True,
        'property': {
            'DatabaseEngine__variable_name': engine.VARIABLE_NAME,
            'DatabaseEngine__database_type': DatabaseType[engine.DATABASE_TYPE].value,
            'DatabaseEngine__driver': DatabaseDriver[engine.DATABASE_TYPE].value,
            'DatabaseEngine__username': engine.USERNAME,
            'DatabaseEngine__password': engine.PASSWORD,
            'DatabaseEngine__host': engine.HOST,
            'DatabaseEngine__port': engine.PORT,
            'DatabaseEngine__query': engine.QUERY,
            'DatabaseEngine__database': engine.DATABASE,
            'DatabaseEngine__connect_timeout': engine.CONNECT_TIMEOUT
        }
    })


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
            'name': 'TransactionHTTPSessionManager',
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
            'name': 'TransactionParameter',
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
    children_links = ElementChildrenDao.select_all_by_parent(snippet_no)
    children = []
    # 添加 HTTP Session 组件
    if use_http_session:
        children.append({
            'name': 'HTTPSessionManager',
            'remark': '',
            'class': 'HTTPSessionManager',
            'enabled': True,
            'property': {}
        })
    # 添加子代
    for link in children_links:
        if child := loads_element(link.CHILD_NO, cache=cache):
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
            element.ELEMENT_CLASS == ElementClass.PYTHON_PRE_PROCESSOR.value
            and not properties.get('PythonPreProcessor__script').strip()
    ):
        return True
    if (
            element.ELEMENT_CLASS == ElementClass.PYTHON_POST_PROCESSOR.value
            and not properties.get('PythonPostProcessor__script').strip()
    ):
        return True
    if (
            element.ELEMENT_CLASS == ElementClass.PYTHON_ASSERTION.value
            and not properties.get('PythonAssertion__script').strip()
    ):
        return True
    return False
