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
from app.modules.script.manager.element_loader import ElementLoader
from app.modules.script.service.execution_service import execute_testplan
from app.tools.exceptions import ServiceError


def execute_testplan(planNo, datasets, useCurrentValue):  # noqa
    with apscheduler.app.app_context():
        execute_testplan(planNo, datasets, useCurrentValue, check_workspace=False)


def execute_collection(collectionNo, datasets, useCurrentValue):  # noqa
    with apscheduler.app.app_context():
        # 查询元素
        collection = test_element_dao.select_by_no(collectionNo)
        if not collection.ENABLED:
            raise ServiceError(msg='元素已禁用')
        if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
            raise ServiceError(msg='仅支持运行测试集合')
        # 根据 collectionNo 递归加载脚本
        script = ElementLoader(collectionNo).loads_tree()
        # 添加变量组件
        if datasets:
            add_variable_dataset(script, datasets=datasets, use_current=useCurrentValue)
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
            raise ServiceError(msg='元素已禁用')
        if worker.ELEMENT_TYPE != ElementType.WORKER.value:
            raise ServiceError(msg='仅支持运行测试用例')
        # 获取 collectionNo
        worker_node = element_children_dao.select_by_child(workerNo)
        if not worker_node:
            raise ServiceError(msg='元素节点不存在')
        # 根据 collectionNo 递归加载脚本
        collection_no = worker_node.PARENT_NO
        script = ElementLoader(collection_no, worker_no=workerNo).loads_tree()
        # 添加变量组件
        if datasets:
            add_variable_dataset(script, datasets=datasets, use_current=useCurrentValue)
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
