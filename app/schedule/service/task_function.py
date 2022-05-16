#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : task_function.py
# @Time    : 2022-05-15 11:57:06
# @Author  : Kelvin.Ye
import traceback

from pymeter.runner import Runner

from app.common.exceptions import ServiceError
from app.extension import apscheduler
from app.script.dao import element_children_dao as ElementChildrenDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.enum import ElementType
from app.script.service.element_loader import add_variable_dataset
from app.script.service.element_loader import loads_tree
from app.script.service.execution_service import run_testplan
from app.utils.log_util import get_logger


log = get_logger(__name__)


def execute_testplan(plan_no, dataset_numbered_list, use_current_value):
    with apscheduler.app.app_context():
        run_testplan(plan_no, dataset_numbered_list, use_current_value)


def execute_collection(collection_no, dataset_numbered_list, use_current_value):
    with apscheduler.app.app_context():
        # 查询元素
        collection = TestElementDao.select_by_no(collection_no)
        if not collection.ENABLED:
            raise ServiceError('元素已禁用')
        if collection.ELEMENT_TYPE != ElementType.COLLECTION.value:
            raise ServiceError('仅支持运行 Collecion 元素')
        # 根据 collectionNo 递归加载脚本
        script = loads_tree(collection_no)
        # 添加变量组件
        if dataset_numbered_list:
            add_variable_dataset(script, dataset_numbered_list, use_current_value)
        # 运行脚本
        try:
            Runner.start([script], throw_ex=True)
        except Exception:
            log.error(traceback.format_exc())


def execute_group(group_no, dataset_numbered_list, use_current_value):
    with apscheduler.app.app_context():
        # 查询元素
        group = TestElementDao.select_by_no(group_no)
        if not group.ENABLED:
            raise ServiceError('元素已禁用')
        if group.ELEMENT_TYPE != ElementType.GROUP.value:
            raise ServiceError('仅支持运行 Group 元素')
        # 获取 collectionNo
        group_parent_link = ElementChildrenDao.select_by_child(group_no)
        if not group_parent_link:
            raise ServiceError('元素父级关联不存在')
        # 根据 collectionNo 递归加载脚本
        collection_no = group_parent_link.PARENT_NO
        script = loads_tree(collection_no, specified_group_no=group_no)
        # 添加变量组件
        if dataset_numbered_list:
            add_variable_dataset(script, dataset_numbered_list, use_current_value)
        # 运行脚本
        try:
            Runner.start([script], throw_ex=True)
        except Exception:
            log.error(traceback.format_exc())


TASK_FUNC = {
    'TESTPLAN': execute_testplan,
    'COLLECTION': execute_collection,
    'GROUP': execute_group
}
