#!/usr/bin/ python3
# @File    : enum.py
# @Time    : 2020/7/3 15:23
# @Author  : Kelvin.Ye
from enum import Enum
from enum import unique


@unique
class ElementType(Enum):
    # 工作空间
    WORKSPACE = 'WORKSPACE'

    # 片段
    SNIPPET = 'SNIPPET'

    # 集合
    COLLECTION = 'COLLECTION'

    # 工作者
    WORKER = 'WORKER'

    # 逻辑控制器
    CONTROLLER = 'CONTROLLER'

    # 配置器
    CONFIG = 'CONFIG'

    # 监听器
    LISTENER = 'LISTENER'

    # 时间控制器
    TIMER = 'TIMER'

    # 取样器
    SAMPLER = 'SAMPLER'

    # 前置处理器
    PREV_PROCESSOR = 'PREV_PROCESSOR'

    # 后置处理器
    POST_PROCESSOR = 'POST_PROCESSOR'

    # 断言器
    ASSERTION = 'ASSERTION' # TODO: rename TEST_ASSERTION


@unique
class ElementClass(Enum):
    # 空间元素
    TEST_WORKSPACE = 'TestWorkspace'

    # 测试集合
    TEST_COLLECTION = 'TestCollection'

    # 片段集合
    TEST_SNIPPET = 'TestSnippet'

    # 工作者
    TEST_WORKER = 'TestWorker'

    # 前置工作者
    SETUP_WORKER = 'SetupWorker'

    # 后置工作者
    TEARDOWN_WORKER = 'TeardownWorker'

    # HTTP取样器
    HTTP_SAMPLER = 'HTTPSampler'

    # Python取样器
    PYTHON_SAMPLER = 'PythonSampler'

    # Snippet取样器
    SNIPPET_SAMPLER = 'SnippetSampler'

    # SQL取样器
    SQL_SAMPLER = 'SQLSampler'

    # HTTP头部配置器
    HTTP_HEADER_MANAGER = 'HTTPHeaderManager'

    # 数据集配置器
    VARIABLE_DATASET = 'VariableDataset'

    # 数据库引擎配置器
    DATABASE_ENGINE = 'DatabaseEngine'

    # 遍历控制器
    FOREACH_CONTROLLER = 'ForeachController'

    # 循环控制器
    LOOP_CONTROLLER = 'LoopController'

    # 重试控制器
    RETRY_CONTROLLER = 'RetryController'

    # If控制器
    IF_CONTROLLER = 'IfController'

    # While控制器
    WHILE_CONTROLLER = 'WhileController'

    # 事务控制器
    TRANSACTION_CONTROLLER = 'TransactionController'

    # Python前置处理器
    PYTHON_PREV_PROCESSOR = 'PythonPrevProcessor'

    # Python后置处理器
    PYTHON_POST_PROCESSOR = 'PythonPostProcessor'

    # JsonPath提取器
    JSON_PATH_EXTRACTOR = 'JsonPathExtractor'

    # Python断言器
    PYTHON_ASSERTION = 'PythonAssertion'

    # JsonPath断言器
    JSON_PATH_ASSERTION = 'JsonPathAssertion'


@unique
class PropertyType(Enum):

    # 字符串类型
    STR = 'STR'

    # 字典类型
    DICT = 'DICT'

    # 列表类型
    LIST = 'LIST'

    def __eq__(self, other):
        return self.value == other if isinstance(other, str) else super().__eq__(other)


@unique
class ElementStatus(Enum):

    # 启用
    ENABLE = True

    # 禁用
    DISABLE = False


@unique
class VariableDatasetType(Enum):

    # 全局变量：与环境无关，与工作空间无关
    GLOBAL = 'GLOBAL'

    # 环境变量：与环境相关，与工作空间相关
    ENVIRONMENT = 'ENVIRONMENT'

    # 自定义变量：与环境无关，与工作空间相关
    CUSTOM = 'CUSTOM'


@unique
class VariableDatasetWeight(Enum):

    # 全局变量
    GLOBAL = 1

    # 空间变量
    WORKSPACE = 2

    # 环境变量
    ENVIRONMENT = 3

    # 自定义变量
    CUSTOM = 4


@unique
class RunningState(Enum):

    # 待运行
    WAITING = 'WAITING'

    # 运行中
    RUNNING = 'RUNNING'

    # 迭代中
    ITERATING = 'ITERATING'

    # 已完成
    COMPLETED = 'COMPLETED'

    # 已中断
    INTERRUPTED = 'INTERRUPTED'

    # 异常
    ERROR = 'ERROR'


@unique
class TestplanState(Enum):

    # 待开始
    INITIAL = 'INITIAL'

    # 测试中
    TESTING = 'TESTING'

    # 已完成
    COMPLETED = 'COMPLETED'


@unique
class TestPhase(Enum):

    # 待测试
    INITIAL = 'INITIAL'

    # 调试
    DEBUG = 'DEBUG'

    # 冒烟测试
    SMOKE_TESTING = 'SMOKE_TESTING'

    # 系统测试
    SYSTEM_TESTING = 'SYSTEM_TESTING'

    # 回归测试
    REGRESSION_TESTING = 'REGRESSION_TESTING'

    # 验收测试
    ACCEPTANCE_TESTING = 'ACCEPTANCE_TESTING'

    # 已完成
    COMPLETED = 'COMPLETED'


@unique
class PasteType(Enum):

    # 复制
    COPY = 'COPY'

    # 剪切
    CUT = 'CUT'


@unique
class DatabaseType(Enum):
    ORACLE = 'oracle'
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'
    MICROSOFT_SQL_SERVER = 'mssql'


@unique
class DatabaseDriver(Enum):
    ORACLE = 'cx_oracle'
    MYSQL = 'mysqlconnector'
    POSTGRESQL = 'psycopg2'
    MICROSOFT_SQL_SERVER = 'pyodbc'


@unique
class ElementOperationType(Enum):
    INSERT = 'INSERT'       # 新增元素
    UPDATE = 'UPDATE'       # 修改元素
    DELETE = 'DELETE'       # 删除元素
    COPY = 'COPY'           # 复制元素（新增元素）
    MOVE = 'MOVE'           # 移动元素（不同父级）
    ORDER = 'ORDER'         # 排序元素（相同父级）
    TRANSFER = 'TRANSFER'   # 转移元素（更改空间）


def is_collection(element):
    return element.ELEMENT_TYPE == ElementType.COLLECTION.value


def is_snippet(element):
    return element.ELEMENT_TYPE == ElementType.SNIPPET.value


def is_worker(element):
    return element.ELEMENT_TYPE == ElementType.WORKER.value


def is_sampler(element):
    return element.ELEMENT_TYPE == ElementType.SAMPLER.value


def is_config(element):
    return element.ELEMENT_TYPE == ElementType.CONFIG.value


def is_controller(element):
    return element.ELEMENT_TYPE == ElementType.CONTROLLER.value


def is_timer(element):
    return element.ELEMENT_TYPE == ElementType.TIMER.value


def is_prev_processor(element):
    return element.ELEMENT_TYPE == ElementType.PREV_PROCESSOR.value


def is_post_processor(element):
    return element.ELEMENT_TYPE == ElementType.POST_PROCESSOR.value


def is_assertion(element):
    return element.ELEMENT_TYPE == ElementType.ASSERTION.value


def is_listener(element):
    return element.ELEMENT_TYPE == ElementType.LISTENER.value


def is_test_collection(element):
    return element.ELEMENT_CLASS == ElementClass.TEST_COLLECTION.value


def is_test_snippet(element):
    return element.ELEMENT_CLASS == ElementClass.TEST_SNIPPET.value


def is_test_worker(element):
    return element.ELEMENT_CLASS == ElementClass.TEST_WORKER.value


def is_setup_worker(element):
    return element.ELEMENT_CLASS == ElementClass.SETUP_WORKER.value


def is_teardown_worker(element):
    return element.ELEMENT_CLASS == ElementClass.TEARDOWN_WORKER.value


def is_pre_post_worker(element):
    return is_setup_worker(element) or is_teardown_worker(element)


def is_http_sampler(element):
    return element.ELEMENT_CLASS == ElementClass.HTTP_SAMPLER.value


def is_sql_sampler(element):
    return element.ELEMENT_CLASS == ElementClass.SQL_SAMPLER.value


def is_snippet_sampler(element):
    return element.ELEMENT_CLASS == ElementClass.SNIPPET_SAMPLER.value


def is_python_prev_processor(element):
    return element.ELEMENT_CLASS == ElementClass.PYTHON_PREV_PROCESSOR.value


def is_python_post_processor(element):
    return element.ELEMENT_CLASS == ElementClass.PYTHON_POST_PROCESSOR.value


def is_python_assertion(element):
    return element.ELEMENT_CLASS == ElementClass.PYTHON_ASSERTION.value


def has_children(element):
    return element.ELEMENT_TYPE in [
        ElementType.COLLECTION.value,
        ElementType.CONTROLLER.value,
        ElementType.WORKER.value
    ]
