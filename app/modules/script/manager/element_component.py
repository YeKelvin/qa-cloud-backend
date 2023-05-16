#!/usr/bin/ python3
# @File    : element_component.py
# @Time    : 2022/9/9 21:50
# @Author  : Kelvin.Ye
from typing import Dict

from app.modules.script.dao import http_header_dao
from app.modules.script.dao import httpheader_template_ref_dao
from app.modules.script.dao import variable_dao
from app.modules.script.dao import variable_dataset_dao
from app.modules.script.enum import DatabaseDriver
from app.modules.script.enum import DatabaseType
from app.modules.script.enum import ElementClass
from app.modules.script.model import TTestElement


def add_flask_sio_result_collector(script: dict, sid: str, result_id: str, result_name: str):
    # 添加 FlaskSIOResultCollector 组件
    script['children'].insert(0, {
        'name': 'Flask SIO Result Collector',
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
        'name': 'Flask DB Result Storage',
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
        'name': 'Flask DB Iteration Storage',
        'remark': '',
        'class': 'FlaskDBIterationStorage',
        'enabled': True,
        'property': {
            'FlaskDBIterationStorage__execution_no': execution_no,
            'FlaskDBIterationStorage__collection_no': collection_no
        }
    })


def add_variable_dataset(script: dict, dataset_nos: list, use_current_value: bool, additional: dict = None):
    # 不存在变量集就忽略了
    if not dataset_nos:
        return

    # 获取变量集
    variables = get_variables(dataset_nos, use_current_value)

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
        'name': 'Variable Dataset',
        'remark': '',
        'class': 'VariableDataset',
        'enabled': True,
        'property': {
            'Arguments__arguments': arguments
        }
    })


def get_variables(dataset_nos: list, use_current_value: bool) -> Dict:
    result = {}
    # 根据列表查询变量集，并根据权重从小到大排序
    dataset_list = variable_dataset_dao.select_list_in_set_orderby_weight(*dataset_nos)
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


def add_http_header_manager(sampler: TTestElement, children: list, cache: Dict[str, dict]):
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
        'name': 'HTTP Header Manager',
        'remark': '',
        'class': 'HTTPHeaderManager',
        'enabled': True,
        'property': {
            'HeaderManager__headers': properties
        }
    })


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
