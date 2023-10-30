#!/usr/bin/ python3
# @File    : task_function.py
# @Time    : 2022-05-15 11:57:06
# @Author  : Kelvin.Ye
from loguru import logger
from pymeter.runner import Runner

from app.extension import apscheduler
from app.modules.script.dao import element_children_dao
from app.modules.script.dao import test_element_dao
from app.modules.script.enum import ElementType
from app.modules.script.manager.element_component import add_variable_dataset
from app.modules.script.manager.element_loader import loads_tree
from app.modules.script.service.execution_service import run_testplan
from app.tools.exceptions import ServiceError


def execute_testplan(planNo, datasets, useCurrentValue):  # noqa
    with apscheduler.app.app_context():
        run_testplan(planNo, datasets, useCurrentValue, check_workspace=False)


def execute_collection(collectionNo, datasets, useCurrentValue):  # noqa
    with apscheduler.app.app_context():
        # 查询元素
        collection = test_element_dao.select_by_no(collectionNo)
        if not collection.ENABLED:
            raise ServiceError('元素已禁用')
        if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
            raise ServiceError('仅支持运行 Collecion 元素')
        # 根据 collectionNo 递归加载脚本
        script = loads_tree(collectionNo)
        # 添加变量组件
        if datasets:
            add_variable_dataset(script, datasets, useCurrentValue)
        # 运行脚本
        try:
            Runner.start([script], throw_ex=True)
        except Exception:
            logger.exception('Exception Occurred')


def execute_worker(workerNo, datasets, useCurrentValue):  # noqa
    with apscheduler.app.app_context():
        # 查询元素
        worker = test_element_dao.select_by_no(workerNo)
        if not worker.ENABLED:
            raise ServiceError('元素已禁用')
        if worker.ELEMENT_TYPE != ElementType.WORKER.value:
            raise ServiceError('仅支持运行 Worker 元素')
        # 获取 collectionNo
        worker_node = element_children_dao.select_by_child(workerNo)
        if not worker_node:
            raise ServiceError('元素节点不存在')
        # 根据 collectionNo 递归加载脚本
        collection_no = worker_node.PARENT_NO
        script = loads_tree(collection_no, required_worker=workerNo)
        # 添加变量组件
        if datasets:
            add_variable_dataset(script, datasets, useCurrentValue)
        # 运行脚本
        try:
            Runner.start([script], throw_ex=True)
        except Exception:
            logger.exception('Exception Occurred')


TASK_FUNC = {
    'TESTPLAN': execute_testplan,
    'COLLECTION': execute_collection,
    'WORKER': execute_worker
}
