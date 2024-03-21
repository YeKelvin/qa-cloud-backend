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


def trigger_testplan_job(plan_no, datasets, use_currvalue):
    with apscheduler.app.app_context():
        execute_testplan(plan_no, datasets, use_currvalue, check_workspace=False)


def trigger_collection_job(collection_no, datasets, use_currvalue):
    with apscheduler.app.app_context():
        # 查询元素
        collection = test_element_dao.select_by_no(collection_no)
        if not collection.ENABLED:
            raise ServiceError(msg='元素已禁用')
        if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
            raise ServiceError(msg='仅支持运行测试集合')
        # 根据 collectionNo 递归加载脚本
        script = ElementLoader(collection_no).loads_tree()
        # 添加变量组件
        if datasets:
            add_variable_dataset(script, datasets=datasets, use_current=use_currvalue)
        # 运行脚本
        try:
            Runner.start([script], throw_ex=True)
        except Exception:
            logger.exception('Exception Occurred')


def trigger_testcase_job(worker_no, datasets, use_currvalue):
    with apscheduler.app.app_context():
        # 查询元素
        worker = test_element_dao.select_by_no(worker_no)
        if not worker.ENABLED:
            raise ServiceError(msg='元素已禁用')
        if worker.ELEMENT_TYPE != ElementType.WORKER.value:
            raise ServiceError(msg='仅支持运行测试用例')
        # 获取 collectionNo
        worker_node = element_children_dao.select_by_child(worker_no)
        if not worker_node:
            raise ServiceError(msg='元素节点不存在')
        # 根据 collectionNo 递归加载脚本
        collection_no = worker_node.PARENT_NO
        script = ElementLoader(collection_no, worker_no=worker_no).loads_tree()
        # 添加变量组件
        if datasets:
            add_variable_dataset(script, datasets=datasets, use_current=use_currvalue)
        # 运行脚本
        try:
            Runner.start([script], throw_ex=True)
        except Exception:
            logger.exception('Exception Occurred')


jobfx = {
    'TESTPLAN': trigger_testplan_job,
    'TESTCASE': trigger_testcase_job,
    'COLLECTION': trigger_collection_job
}
