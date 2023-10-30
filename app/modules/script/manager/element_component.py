#!/usr/bin/ python3
# @File    : element_component.py
# @Time    : 2022/9/9 21:50
# @Author  : Kelvin.Ye
from app.modules.script.dao import variable_dao
from app.modules.script.dao import variable_dataset_dao


def create_test_collection(
    name,
    desc='',
    serialize_workers='true',
    delay='0',
    children=None
):
    return {
        'name': name,
        'desc': desc,
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
    desc='',
    on_sample_error='start_next_thread',
    number_of_threads='1',
    loops='1',
    continue_forever='false',
    children=None
):
    return {
        'name': name,
        'desc': desc,
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


def create_http_session_manager(name='HTTP会话管理器', desc=''):
    return {
        'name': name,
        'desc': desc,
        'class': 'HTTPSessionManager',
        'enabled': True,
        'property': {}
    }


def create_transaction_http_session_manager(name='事务HTTP会话管理器', desc=''):
    return {
        'name': name,
        'desc': desc,
        'class': 'TransactionHTTPSessionManager',
        'enabled': True,
        'property': {}
    }


def create_argument(name, value):
    return {
        'class': 'Argument',
        'property': {
            'Argument__name': name,
            'Argument__value': value,
        },
    }


def create_transaction_parameter(arguments, name='事务参数', desc=''):
    return {
        'name': name,
        'desc': desc,
        'class': 'TransactionParameter',
        'enabled': True,
        'property': {
            'Arguments__arguments': arguments
        }
    }

def create_http_header(name, value):
    return {
        'class': 'HTTPHeader',
        'property': {
            'Header__name': name,
            'Header__value': value
        }
    }


def create_http_header_manager(headers, name='HTTP请求头管理器', desc=''):
    return {
        'name': name,
        'desc': desc,
        'class': 'HTTPHeaderManager',
        'enabled': True,
        'property': {
            'HeaderManager__headers': headers
        }
    }


def create_variable_dataset(arguments, name='变量集', desc=''):
    return {
        'name': name,
        'desc': desc,
        'class': 'VariableDataset',
        'enabled': True,
        'property': {
            'Arguments__arguments': arguments
        }
    }


def add_flask_sio_result_collector(script: dict, socket_id: str, result_id: str, result_name: str):
    # 添加 FlaskSIOResultCollector 组件
    script['children'].insert(0, {
        'name': 'Flask实时结果收集器',
        'desc': '',
        'class': 'FlaskSIOResultCollector',
        'enabled': True,
        'property': {
            'FlaskSIOResultCollector__socket_id': socket_id,
            'FlaskSIOResultCollector__result_id': result_id,
            'FlaskSIOResultCollector__result_name': result_name,
        }
    })


def add_flask_db_result_storage(script: dict, report_no: str, collection_no: str):
    # 添加 FlaskDBResultStorage 组件
    script['children'].insert(0, {
        'name': 'Flask数据库结果存储器',
        'desc': '',
        'class': 'FlaskDBResultStorage',
        'enabled': True,
        'property': {
            'FlaskDBResultStorage__report_no': report_no,
            'FlaskDBResultStorage__collection_no': collection_no
        }
    })


def add_flask_db_iteration_storage(script: dict, execution_no: str, collection_no: str):
    # 添加 FlaskDBIterationStorage 组件
    script['children'].insert(0, {
        'name': 'Flask数据库迭代存储器',
        'desc': '',
        'class': 'FlaskDBIterationStorage',
        'enabled': True,
        'property': {
            'FlaskDBIterationStorage__execution_no': execution_no,
            'FlaskDBIterationStorage__collection_no': collection_no
        }
    })


def add_variable_dataset(script: dict, datasets: list, use_current_value: bool=False, additional: dict = None):
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
    arguments = [create_argument(name, value) for name, value in variables.items()]

    # 添加 VariableDataset 组件
    script['children'].insert(0, create_variable_dataset(arguments))


def get_variables(datasets: list, use_current_value: bool) -> dict:
    result = {}
    # 根据列表查询变量集，并根据权重从小到大排序
    dataset_list = variable_dataset_dao.select_list_in_no(*datasets)
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


def add_http_session_manager(each_clear: bool, children: list):
    children.append({
        'name': 'HTTP会话管理器',
        'desc': '',
        'class': 'HTTPSessionManager',
        'enabled': True,
        'property': {
            'HTTPSessionManager__clear_each_iteration': 'true' if each_clear else 'false'
        }
    })
