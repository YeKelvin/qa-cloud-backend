#!/usr/bin/ python3
# @File    : element_loader.py
# @Time    : 2021-10-02 13:04:49
# @Author  : Kelvin.Ye
from loguru import logger

from app.database import db_query
from app.modules.script.dao import database_config_dao
from app.modules.script.dao import element_children_dao
from app.modules.script.dao import http_header_dao
from app.modules.script.dao import test_element_dao
from app.modules.script.enum import DatabaseDriver
from app.modules.script.enum import DatabaseType
from app.modules.script.enum import ElementClass
from app.modules.script.enum import is_snippet_sampler
from app.modules.script.enum import is_test_collection
from app.modules.script.enum import is_test_snippet
from app.modules.script.manager.element_component import add_http_session_manager
from app.modules.script.manager.element_component import create_argument
from app.modules.script.manager.element_component import create_http_header
from app.modules.script.manager.element_component import create_http_header_manager
from app.modules.script.manager.element_component import create_http_session_manager
from app.modules.script.manager.element_component import create_test_collection
from app.modules.script.manager.element_component import create_test_worker
from app.modules.script.manager.element_component import create_transaction_http_session_manager
from app.modules.script.manager.element_component import create_transaction_parameter
from app.modules.script.manager.element_manager import get_element_property
from app.modules.script.manager.element_manager import get_workspace_no
from app.modules.script.model import TElementComponent
from app.modules.script.model import TTestElement
from app.tools.exceptions import ServiceError
from app.tools.validator import check_exists


class CheckError(Exception):
    pass


def test_worker_checker(**kwargs):
    loader: 'ElementLoader' = kwargs.get('loader')
    element: TTestElement = kwargs.get('element')
    # 加载指定的用例，如果当前元素非指定的用例时返回None
    if element.number != loader.required_worker:
        logger.debug(f'元素名称:[ {element.name} ] 非指定的用例, 无需加载')
        raise CheckError()


def python_prev_processor_checker(**kwargs):
    element: TTestElement = kwargs.get('element')
    props: dict = kwargs.get('props')
    # 过滤空代码的 Python 组件
    if not props.get('PythonPrevProcessor__script').strip():
        logger.debug(f'元素名称:[ {element.name} ] Python代码为空, 无需加载')
        raise CheckError()


def python_post_processor_checker(**kwargs):
    element: TTestElement = kwargs.get('element')
    props: dict = kwargs.get('props')
    # 过滤空代码的 Python 组件
    if not props.get('PythonPostProcessor__script').strip():
        logger.debug(f'元素名称:[ {element.name} ] Python代码为空, 无需加载')
        raise CheckError()


def python_test_assertion_checker(**kwargs):
    element: TTestElement = kwargs.get('element')
    props: dict = kwargs.get('props')
    # 过滤空代码的 Python 组件
    if not props.get('PythonAssertion__script').strip():
        logger.debug(f'元素名称:[ {element.name} ] Python代码为空, 无需加载')
        raise CheckError()


def test_collection_loader(**kwargs):
    loader: 'ElementLoader' = kwargs.get('loader')
    element: TTestElement = kwargs.get('element')
    children: list = kwargs.get('children')
    components: list = kwargs.get('components')
    # 添加元素组件
    loader.add_element_components(element.number, children, offlines=components)


def test_worker_loader(**kwargs):
    loader: 'ElementLoader' = kwargs.get('loader')
    element: TTestElement = kwargs.get('element')
    children: list = kwargs.get('children')
    components: list = kwargs.get('components')
    # 添加HTTP会话管理器
    if element.attrs.get('Worker__use_http_session', False):
        add_http_session_manager(element.attrs.get('Worker__clear_http_session_each_iteration', False), children)
    # 添加元素组件
    loader.add_element_components(element.number, children, offlines=components)


def setup_worker_loader(**kwargs):
    loader: 'ElementLoader' = kwargs.get('loader')
    element: TTestElement = kwargs.get('element')
    children: list = kwargs.get('children')
    components: list = kwargs.get('components')
    # 添加HTTP会话管理器
    if element.attrs.get('Worker__use_http_session', False):
        add_http_session_manager(element.attrs.get('Worker__clear_http_session_each_iteration', False), children)
    # 添加元素组件
    loader.add_element_components(element.number, children, offlines=components)


def teardown_worker_loader(**kwargs):
    loader: 'ElementLoader' = kwargs.get('loader')
    element: TTestElement = kwargs.get('element')
    children: list = kwargs.get('children')
    components: list = kwargs.get('components')
    # 添加HTTP会话管理器
    if element.attrs.get('Worker__use_http_session', False):
        add_http_session_manager(element.attrs.get('Worker__clear_http_session_each_iteration', False), children)
    # 添加元素组件
    loader.add_element_components(element.number, children, offlines=components)


def http_sampler_loader(**kwargs):
    loader: 'ElementLoader' = kwargs.get('loader')
    element: TTestElement = kwargs.get('element')
    children: list = kwargs.get('children')
    components: list = kwargs.get('components')
    # 添加HTTP请求头管理器
    loader.add_http_header_manager(element.attrs, children)
    # 添加元素组件
    loader.add_element_components(element.number, children, offlines=components)


def sql_sampler_loader(**kwargs):
    loader: 'ElementLoader' = kwargs.get('loader')
    element: TTestElement = kwargs.get('element')
    props: dict = kwargs.get('props')
    # 添加数据库引擎配置器
    loader.add_database_engine(element.attrs.get('SQLSampler__engine_no'), props)


checkers = {
    # worker
    'TestWorker': test_worker_checker,
    # python
    'PythonPrevProcessor': python_prev_processor_checker,
    'PythonPostProcessor': python_post_processor_checker,
    'PythonAssertion': python_test_assertion_checker
}

loaders ={
    # collection
    'TestCollection': setup_worker_loader,
    # worker
    'TestWorker': test_worker_loader,
    'SetupWorker': setup_worker_loader,
    'TeardownWorker': teardown_worker_loader,
    # sampler
    'HTTPSampler': http_sampler_loader,
    'SQLSampler': sql_sampler_loader
}


class ElementLoader:

    def __init__(self, root_no, offlines=None, required_worker=None, required_sampler=None):
        # 数据库缓存
        self.caches = {} # { ElementClass: {} }
        # 离线数据
        self.offlines = offlines or {}
        # 根元素编号
        self.root_no = root_no
        # 根元素对象
        self.root_element = self.get_root_element()
        # 根元素所在的空间编号
        self.workspace_no = get_workspace_no(root_no)
        # 空间元素对象
        self.workspace_element:TTestElement = None
        # 指定的用例编号
        self.required_worker = required_worker
        # 指定的请求编号
        self.required_sampler = required_sampler
        # 寻找用例标识
        self.worker_found = False
        # 寻找请求标识
        self.sampler_found = False
        # 全局配置器
        self.global_config = {} # { ElementClass: [] }

    def get_root_element(self) -> TTestElement:
        root, _, _ = self.get_offline_element(self.root_no)
        root = root or test_element_dao.select_by_no(self.root_no)
        check_exists(root, error_msg='根元素不存在')
        return root

    def get_workspace_element(self) -> (TTestElement, list):
        ws, _, compos = self.get_offline_element(self.workspace_no)
        components =[]
        if compos:
            # 读取离线数据
            for component in compos:
                component_no = component['elementNo']
                self.offlines[component_no] = component
                components.append(TElementComponent(ELEMENT_NO=component_no))
        if not ws:
            # 读取后端数据
            ws = test_element_dao.select_by_no(self.workspace_no)
            check_exists(ws, error_msg='空间元素不存在')
            components = (
                db_query(TElementComponent.ELEMENT_NO, TElementComponent.ELEMENT_SORT)
                .filter(TElementComponent.DELETED == 0, TElementComponent.PARENT_NO == self.workspace_no)
                .order_by(TElementComponent.ELEMENT_SORT.asc())
                .all()
            )
        compos = []
        for component in components:
            if element := self.loads_element(component.ELEMENT_NO):
                element['level'] = 0  # 给空间组件添加层级
                compos.append(element)

        return ws, compos

    def loads_tree(self):
        """根据元素编号加载脚本"""
        logger.debug(
            f'开始加载脚本'
            f'\n指定的用例编号:[ {self.required_worker} ]'
            f'\n指定的请求编号:[ {self.required_sampler} ]'
        )
        # 加载脚本
        if is_test_collection(self.root_element):
            return self.loads_test_collection()
        elif is_test_snippet(self.root_element):
            return self.loads_test_snippet()
        else:
            raise ServiceError('元素非法')

    def loads_test_collection(self):
        # 递归加载元素
        collection = self.loads_element(self.root_no)
        if not collection:
            raise ServiceError('脚本异常，请联系管理员')
        # 添加全局配置
        for configs in self.global_config.values():
            for config in configs:
                collection['children'].insert(0, config)
        # 获取配置属性和脚本属性
        attributes = collection.get('attribute')
        properties = collection.get('property')
        exclude_workspace = attributes.get('TestCollection__exclude_workspace', False)
        # 添加空间组件（配置器、前置处理器、后置处理器、测试断言器）
        if not exclude_workspace:
            # 获取空间元素和空间组件
            self.workspace_element, components = self.get_workspace_element()
            # 添加空间组件至脚本顶部
            for component in components[::-1]:
                collection['children'].insert(0, component)
            # 合并空间和集合的运行策略
            self.merge_running_strategy(properties)

        return collection

    def merge_running_strategy(self, root_propery):
        # 查询集合运行策略
        root_strategy = root_propery.get('TestCollection__running_strategy', {}) or {}
        # 优先使用集合的运行策略
        if root_strategy.get('reverse'):
            return
        # 集合的运行策略没有设置时，合并空间的运行策略
        workspace_strategy = self.workspace_element.attrs.get('running_strategy', {}) or {}
        if workspace_reverse := workspace_strategy.get('reverse', []):
            root_strategy['reverse'] = workspace_reverse
            root_propery['TestCollection__running_strategy'] = root_strategy
        else:
            return

    def loads_test_snippet(self):
        # 递归查询子代，并根据序号正序排序
        nodes = element_children_dao.select_all_by_parent(self.root_no)
        children = []
        # 添加 HTTP Session 组件
        if self.root_element.attrs.get('use_http_session', False):
            children.append(create_http_session_manager())
        # 添加子代
        for node in nodes:
            if child := self.loads_element(node.ELEMENT_NO):
                children.append(child)
        # 创建一个临时的 Collection
        # TODO: 需要增加一个参数来控制，是否排除空间组件
        return create_test_collection(
            name=self.root_element.name,
            children=[
                # 创建一个临时的 Worker
                create_test_worker(name=self.root_element.name, children=children)
            ]
        )

    def get_offline_element(self, element_no) -> (TTestElement, dict, list):
        """从离线数据中读取元素信息，包含TTestElement对象，元素属性和元素组件"""
        if offline := self.offlines.get(element_no):
            # 组装元素信息
            element = TTestElement(
                ELEMENT_NO=element_no,
                ELEMENT_NAME=offline.get('elementName'),
                ELEMENT_DESC=offline.get('elementDesc'),
                ELEMENT_TYPE=offline.get('elementType'),
                ELEMENT_CLASS=offline.get('elementClass'),
                ELEMENT_ATTRS=offline.get('elementAttrs'),
                ENABLED=offline.get('enabled')
            )
            # 分类获取组件列表
            components = offline.get('elementCompos', {})
            conf_list = components.get('confList', []) or []
            prev_list = components.get('prevList', []) or []
            post_list = components.get('postList', []) or []
            test_list = components.get('testList', []) or []
            # 返回元素信息、元素属性和元素组件
            return element, offline.get('elementProps', {}), conf_list + prev_list + post_list + test_list
        else:
            return None, {}, []

    def loads_element(self, element_no) -> dict:
        """根据元素编号加载元素数据"""
        # 优先从离线数据中获取元素
        element, properties, components = self.get_offline_element(element_no)
        if not element:
            # 查询元素
            element = test_element_dao.select_by_no(element_no)
            check_exists(element, error_msg='元素不存在')
            properties = get_element_property(element_no)
        # 元素为禁用状态时返回None
        if not element.enabled:
            logger.debug(f'元素名称:[ {element.name} ] 元素已禁用, 无需加载')
            return None
        # 元素子代
        children = []
        # 校验组件
        try:
            checker = checkers.get(element.clazz)
            checker and not checker(loader=self, element=element, props=properties)
        except CheckError:
            return None
        # 加载组件
        loader = loaders.get(element.clazz)
        loader and loader(loader=self, element=element, props=properties, children=children, components=components)
        # 非片段请求时直接添加子代
        if not is_snippet_sampler(element):
            children.extend(self.loads_children(element_no))
        # 片段请求则查询片段内容
        else:
            children.extend(self.loads_snippet_sampler(element.attrs))
        # 组装元素信息并返回
        return {
            'name': element.name,
            'desc': element.desc,
            'class': (
                ElementClass.TRANSACTION_CONTROLLER.value
                if is_snippet_sampler(element)
                else element.clazz
            ),
            'enabled': element.enabled,
            'property': properties,
            'children': children,
            'attribute': element.attrs
        }

    def loads_children(self, element_no):
        # 查询子代，并根据序号正序排序
        nodes = element_children_dao.select_all_by_parent(element_no)
        children = []
        # 添加子代
        for node in nodes:
            if self.sampler_found:
                break
            # 加载子代元素
            if child := self.loads_element(node.ELEMENT_NO):
                children.append(child)
            else:
                continue
            # 找到指定的 Sampler 就返回
            if node.ELEMENT_NO == self.required_sampler:
                self.sampler_found = True
        return children

    def add_element_components(self, element_no, children: list, offlines: list=None):
        components = []
        if offlines:
            # 读取离线数据
            for component in offlines:
                component_no = component['elementNo']
                self.offlines[component_no] = component
                components.append(TElementComponent(ELEMENT_NO=component_no))
        else:
            # 读取数据库
            components = (
                db_query(TElementComponent.ELEMENT_NO, TElementComponent.ELEMENT_SORT)
                .filter(TElementComponent.DELETED == 0, TElementComponent.PARENT_NO == element_no)
                .order_by(TElementComponent.ELEMENT_SORT.asc())
                .all()
            )
        for el in components:
            if component := self.loads_element(el.ELEMENT_NO):
                children.append(component)

    def loads_snippet_sampler(self, sampler_attrs):
        # 根据片段编号加载片段集合（片段请求在脚本中其实是事务，这里做了一层转换）
        snippet_no = sampler_attrs.get('SnippetSampler__snippet_no', None)
        if not snippet_no:
            raise ServiceError('片段编号不能为空')
        # 加载测试片段
        transaction = self.loads_element(snippet_no)
        if not transaction:
            return
        trans_children = transaction.get('children')
        if not trans_children:
            return
        trans_attrs = transaction.get('attribute', {})
        # 片段形参
        parameters = trans_attrs.get('TestSnippet__parameters', [])
        # 片段实参
        arguments = sampler_attrs.get('SnippetSampler__arguments', [])
        # 是否使用形参默认值
        use_default_val = sampler_attrs.get('SnippetSampler__use_default_val', False)
        # 是否使用HTTP会话，并添加 TransactionHTTPSessionManager 组件
        if trans_attrs.get('TestSnippet__use_http_session', False):
            trans_children.insert(0, create_transaction_http_session_manager())
        # 添加 TransactionParameter 组件
        if arguments or parameters:
            elements = []
            if use_default_val:  # 使用测试片段的默认值
                elements.extend(
                    create_argument(name=param['name'], value=param['default'])
                    for param in parameters
                )
            else:  # 使用自定义的参数值
                args = {arg['name']: arg['value'] for arg in arguments}
                elements.extend(
                    create_argument(name=param['name'], value=args.get(param['name']) or param['default'])
                    for param in parameters
                )
            trans_children.insert(0, create_transaction_parameter(elements))
        # 返回片段子代
        return trans_children


    def add_http_header_manager(self, attributes: dict, children: list):
        # 查询请求头模板
        template_refs = attributes.get('HTTPSampler__header_template_refs', [])

        # 没有模板时直接跳过
        if not template_refs:
            return

        # 获取请求头管理器缓存
        cache__header_manager = self.caches.get(ElementClass.HTTP_HEADER_MANAGER.value, {})
        if not cache__header_manager:
            self.caches[ElementClass.HTTP_HEADER_MANAGER.value] = cache__header_manager

        # 遍历添加请求头
        properties = []
        for ref in template_refs:
            # 先查缓存
            cache__headers = cache__header_manager.get(ref.TEMPLATE_NO, [])
            if not cache__headers:
                headers = http_header_dao.select_all_by_template(ref.TEMPLATE_NO)
                for header in headers:
                    cache__headers.append(create_http_header(name=header.HEADER_NAME, value=header.HEADER_VALUE))
                cache__header_manager[ref.TEMPLATE_NO] = cache__headers
            properties.extend(cache__headers)

        # 添加 HTTPHeaderManager 组件
        children.append(create_http_header_manager(properties))

    def add_database_engine(self, engine_no, properties: dict):
        # 查询数据库引擎
        engine = database_config_dao.select_by_no(engine_no)
        check_exists(engine, error_msg='数据库引擎不存在')
        # 实时将引擎变量名称写入元素属性中
        properties['SQLSampler__engine_name'] = engine.VARIABLE_NAME
        engines = self.global_config.get(ElementClass.DATABASE_ENGINE.value, [])
        if not engines:
            self.global_config[ElementClass.DATABASE_ENGINE.value] = engines
        engines.append({
            'name': engine.DATABASE_NAME,
            'desc': engine.DATABASE_DESC,
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
