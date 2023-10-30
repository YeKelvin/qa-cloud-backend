#!/usr/bin python3
# @File    : debug_service.py
# @Time    : 2023-05-16 16:29:44
# @Author  : Kelvin.Ye
from app.modules.script.dao import element_children_dao
from app.modules.script.dao import test_element_dao
from app.modules.script.enum import ElementType
from app.modules.script.enum import is_test_snippet
from app.modules.script.manager import element_loader
from app.modules.script.manager.element_component import add_variable_dataset
from app.tools.exceptions import ServiceError
from app.tools.service import http_service


@http_service
def query_collection_json(req):
    # 查询元素
    collection = test_element_dao.select_by_no(req.collectionNo)
    if not collection.ENABLED:
        raise ServiceError('元素已禁用')
    if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
        raise ServiceError('仅支持 Collecion 元素')
    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_tree(req.collectionNo)
    # 添加变量组件
    add_variable_dataset(script, req.datasets, req.useCurrentValue)
    return script


@http_service
def query_worker_json(req):
    # 查询元素
    worker = test_element_dao.select_by_no(req.workerNo)
    if not worker.ENABLED:
        raise ServiceError('元素已禁用')
    if worker.ELEMENT_TYPE != ElementType.WORKER.value:
        raise ServiceError('仅支持 Worker 元素')
    # 获取 collectionNo
    worker_node = element_children_dao.select_by_child(req.workerNo)
    if not worker_node:
        raise ServiceError('元素节点不存在')
    collection_no = worker_node.PARENT_NO
    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_tree(collection_no, required_worker=req.workerNo)
    # 添加变量组件
    add_variable_dataset(script, req.datasets, req.useCurrentValue)
    return script


@http_service
def query_snippet_json(req):
    # 查询元素
    collection = test_element_dao.select_by_no(req.collectionNo)
    if not collection.ENABLED:
        raise ServiceError('元素已禁用')
    if not is_test_snippet(collection):
        raise ServiceError('仅支持 TestSnippet 元素')
    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_test_snippet(
        collection.ELEMENT_NO,
        collection.ELEMENT_NAME,
        collection.ELEMENT_DESC
    )
    # 添加变量组件
    add_variable_dataset(script, req.datasets, req.useCurrentValue, req.variables)
    return script
