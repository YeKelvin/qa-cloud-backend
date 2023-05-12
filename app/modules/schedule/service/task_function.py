#!/usr/bin/ python3
# @File    : task_function.py
# @Time    : 2022-05-15 11:57:06
# @Author  : Kelvin.Ye
from loguru import logger
from pymeter.runner import Runner

from app.extension import apscheduler
from app.modules.script.dao import element_children_dao as ElementChildrenDao
from app.modules.script.dao import test_element_dao as TestElementDao
from app.modules.script.enum import ElementType
from app.modules.script.service.element_component import add_variable_dataset
from app.modules.script.service.element_loader import loads_tree
from app.modules.script.service.execution_service import run_testplan
from app.tools.exceptions import ServiceError


def execute_testplan(planNo, datasetNos, useCurrentValue):  # noqa
    with apscheduler.app.app_context():
        run_testplan(planNo, datasetNos, useCurrentValue, check_workspace=False)


def execute_collection(collectionNo, datasetNos, useCurrentValue):  # noqa
    with apscheduler.app.app_context():
        # 查询元素
        collection = TestElementDao.select_by_no(collectionNo)
        if not collection.ENABLED:
            raise ServiceError('元素已禁用')
        if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
            raise ServiceError('仅支持运行 Collecion 元素')
        # 根据 collectionNo 递归加载脚本
        script = loads_tree(collectionNo)
        # 添加变量组件
        if datasetNos:
            add_variable_dataset(script, datasetNos, useCurrentValue)
        # 运行脚本
        try:
            Runner.start([script], throw_ex=True)
        except Exception:
            logger.exception('Exception Occurred')


def execute_group(groupNo, datasetNos, useCurrentValue):  # noqa
    with apscheduler.app.app_context():
        # 查询元素
        group = TestElementDao.select_by_no(groupNo)
        if not group.ENABLED:
            raise ServiceError('元素已禁用')
        if group.ELEMENT_TYPE != ElementType.GROUP.value:
            raise ServiceError('仅支持运行 Group 元素')
        # 获取 collectionNo
        group_parent_relation = ElementChildrenDao.select_by_child(groupNo)
        if not group_parent_relation:
            raise ServiceError('元素父级关联不存在')
        # 根据 collectionNo 递归加载脚本
        collection_no = group_parent_relation.PARENT_NO
        script = loads_tree(collection_no, specified_group_no=groupNo)
        # 添加变量组件
        if datasetNos:
            add_variable_dataset(script, datasetNos, useCurrentValue)
        # 运行脚本
        try:
            Runner.start([script], throw_ex=True)
        except Exception:
            logger.exception('Exception Occurred')


TASK_FUNC = {
    'TESTPLAN': execute_testplan,
    'COLLECTION': execute_collection,
    'GROUP': execute_group
}
