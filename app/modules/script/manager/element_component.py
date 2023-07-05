#!/usr/bin/ python3
# @File    : element_component.py
# @Time    : 2022/9/9 21:50
# @Author  : Kelvin.Ye
from typing import Dict

from app.modules.script.dao import database_config_dao
from app.modules.script.dao import http_header_dao
from app.modules.script.dao import httpheader_template_ref_dao
from app.modules.script.dao import variable_dao
from app.modules.script.dao import variable_dataset_dao
from app.modules.script.enum import DatabaseDriver
from app.modules.script.enum import DatabaseType
from app.modules.script.enum import ElementClass
from app.modules.script.manager.element_context import loads_cache
from app.modules.script.manager.element_context import loads_configurator
from app.modules.script.model import TTestElement
from app.tools.validator import check_exists


def add_flask_sio_result_collector(script: dict, sid: str, result_id: str, result_name: str):
    # 添加 FlaskSIOResultCollector 组件
    script['children'].insert(0, {
        'name': 'Flask实时结果收集器',
        'remark': '',
        'class': 'FlaskSIOResultCollector',
        'enabled': True,
        'property': {
            'FlaskSIOResultCollector__target_sid': sid,
            'FlaskSIOResultCollector__result_id': result_id,
            'FlaskSIOResultCollector__result_name': result_name,
        }
    })


def add_flask_db_result_storage(script: dict, report_no, collection_no):
    # 添加 FlaskDBResultStorage 组件
    script['children'].insert(0, {
        'name': 'Flask数据库结果存储器',
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
        'name': 'Flask数据库迭代存储器',
        'remark': '',
        'class': 'FlaskDBIterationStorage',
        'enabled': True,
        'property': {
            'FlaskDBIterationStorage__execution_no': execution_no,
            'FlaskDBIterationStorage__collection_no': collection_no
        }
    })


def add_variable_dataset(script: dict, datasets: list, use_current_value: bool, additional: dict = None):
    # 不存在变量集就忽略了
    if not datasets:
        return

    # 获取变量集
    variables = get_variables(datasets, use_current_value)

    # 添加额外的变量
    if additional:
        for name, value in additional.items():
            # 如果额外变量的值还是变量，则先在变量集中查找真实值并替换
            if value.startswith('${') and value.endswith('}'):
                variables[name] = variables.get(value[2:-1])
            else:
                variables[name] = value

    # 组装为元素
    arguments = [
        {
            'class': 'Argument',
            'property':
                {
                    'Argument__name': name,
                    'Argument__value': value
                }
        }
        for name, value in variables.items()
    ]

    # 添加 VariableDataset 组件
    script['children'].insert(0, {
        'name': '变量集',
        'remark': '',
        'class': 'VariableDataset',
        'enabled': True,
        'property': {
            'Arguments__arguments': arguments
        }
    })


def get_variables(datasets: list, use_current_value: bool) -> Dict:
    result = {}
    # 根据列表查询变量集，并根据权重从小到大排序
    dataset_list = variable_dataset_dao.select_list_in_set_orderby_weight(*datasets)
    if not dataset_list:
        return result

    for dataset in dataset_list:
        # 查询变量列表
        variables = variable_dao.select_all_by_dataset(dataset.DATASET_NO)

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
    cache = loads_cache.get()
    # 查询元素关联的请求头模板
    refs = httpheader_template_ref_dao.select_all_by_sampler(sampler.ELEMENT_NO)

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
            headers = http_header_dao.select_all_by_template(ref.TEMPLATE_NO)
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
        'name': 'HTTP请求头管理器',
        'remark': '',
        'class': 'HTTPHeaderManager',
        'enabled': True,
        'property': {
            'HeaderManager__headers': properties
        }
    })


def add_database_engine(engine_no, properties: dict):
    # 查询数据库引擎
    engine = database_config_dao.select_by_no(engine_no)
    check_exists(engine, error_msg='数据库引擎不存在')
    # 实时将引擎变量名称写入元素属性中
    properties['SQLSampler__engine_name'] = engine.VARIABLE_NAME
    # TODO: 要优化
    configurator = loads_configurator.get()
    engines = configurator.get(ElementClass.DATABASE_ENGINE.value, [])
    if not engines:
        configurator[ElementClass.DATABASE_ENGINE.value] = engines
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


def add_http_session_manager(clear_each_iteration: bool, children: list):
    children.append({
        'name': 'HTTP会话管理器',
        'remark': '',
        'class': 'HTTPSessionManager',
        'enabled': True,
        'property': {
            'HTTPSessionManager__clear_each_iteration': 'true' if clear_each_iteration else 'false'
        }
    })


def create_test_collection(
    name,
    remark='',
    serialize_workers='true',
    delay='0',
    children=None
):
    return {
        'name': name,
        'remark': remark,
        'class': 'TestCollection',
        'enabled': True,
        'property': {
            'TestCollection__serialize_workers': serialize_workers,
            'TestCollection__delay': delay
        },
        'children': children
    }


def create_test_worker(
    name,
    remark='',
    on_sample_error='start_next_thread',
    number_of_threads='1',
    loops='1',
    continue_forever='false',
    children=None
):
    return {
        'name': name,
        'remark': remark,
        'class': 'TestWorker',
        'enabled': True,
        'property': {
            'TestWorker__on_sample_error': on_sample_error,
            'TestWorker__number_of_threads': number_of_threads,
            'TestWorker__start_interval': '',
            'TestWorker__main_controller': {
                'class': 'LoopController',
                'property': {
                    'LoopController__loops': loops,
                    'LoopController__continue_forever': continue_forever
                }
            }
        },
        'children': children
    }
