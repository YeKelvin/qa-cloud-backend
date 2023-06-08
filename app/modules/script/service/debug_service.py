#!/usr/bin python3
# @File    : debug_service.py
# @Time    : 2023-05-16 16:29:44
# @Author  : Kelvin.Ye
from app.modules.script.dao import element_children_dao
from app.modules.script.dao import test_element_dao
from app.modules.script.enum import ElementType
from app.modules.script.enum import is_snippet_collection
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
    add_variable_dataset(script, req.datasetNos, req.useCurrentValue)
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
    worker_parent_relation = element_children_dao.select_by_child(req.workerNo)
    if not worker_parent_relation:
        raise ServiceError('元素父级关联不存在')
    collection_no = worker_parent_relation.PARENT_NO
    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_tree(collection_no, specify_worker_no=req.workerNo)
    # 添加变量组件
    add_variable_dataset(script, req.datasetNos, req.useCurrentValue)
    return script


@http_service
def query_snippets_json(req):
    # 查询元素
    collection = test_element_dao.select_by_no(req.collectionNo)
    if not collection.ENABLED:
        raise ServiceError('元素已禁用')
    if not is_snippet_collection(collection):
        raise ServiceError('仅支持 SnippetCollection 元素')
    # 根据 collectionNo 递归加载脚本
    script = element_loader.loads_snippet_collecion(
        collection.ELEMENT_NO,
        collection.ELEMENT_NAME,
        collection.ELEMENT_REMARK
    )
    # 添加变量组件
    add_variable_dataset(script, req.datasetNos, req.useCurrentValue, req.variables)
    return script
