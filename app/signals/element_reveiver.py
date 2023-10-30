#!/usr/bin python3
# @File    : element_reveiver.py
# @Time    : 2023-09-26 16:27:14
# @Author  : Kelvin.Ye
from contextvars import ContextVar

from flask import request
from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.database import db_execute
from app.modules.script.dao import test_element_dao
from app.modules.script.dao import workspace_script_dao
from app.modules.script.enum import ElementOperationType
from app.modules.script.enum import ElementType
from app.modules.script.model import TElementChangelog
from app.modules.script.model import TElementChildren
from app.modules.script.model import TElementComponent
from app.modules.script.model import TTestElement
from app.signals import element_copied_signal
from app.signals import element_created_signal
from app.signals import element_modified_signal
from app.signals import element_moved_signal
from app.signals import element_removed_signal
from app.signals import element_sorted_signal
from app.signals import element_transferred_signal
from app.tools import localvars
from app.tools.exceptions import ServiceError
from app.utils.time_util import datetime_now_by_utc8


# 0代表当前线程没有值，需要初始化
localvar__element_nodes = ContextVar('ELEMENT_NODES', default=0)
localvar__root_no = ContextVar('ROOT_NO', default=0)
localvar__case_no = ContextVar('CASE_NO', default=0)
localvar__parents = ContextVar('PARENTS', default=0)


TRootElement: TTestElement = aliased(TTestElement)
TParentElement: TTestElement = aliased(TTestElement)


def get_workspace_no():
    """获取当前空间编号"""
    if workspace_no := request.headers.get('x-workspace-no'):
        return workspace_no
    else:
        raise ServiceError('获取空间编号失败')


def is_root_node(element_no):
    return workspace_script_dao.select_by_script(element_no)


def get_child_node(element_no):
    stmt = (
        select(
            TElementChildren.ROOT_NO,
            TElementChildren.PARENT_NO,
            TRootElement.ELEMENT_TYPE.label('ROOT_TYPE'),
            TParentElement.ELEMENT_TYPE.label('PARENT_TYPE')
        )
        .join(TRootElement, TRootElement.ELEMENT_NO == TElementChildren.ROOT_NO)
        .join(TParentElement, TParentElement.ELEMENT_NO == TElementChildren.PARENT_NO)
        .where(TElementChildren.ELEMENT_NO == element_no)
    )
    return db_execute(stmt).first()


def get_component_node(element_no):
    stmt = (
        select(
            TElementComponent.ROOT_NO,
            TElementComponent.PARENT_NO,
            TRootElement.ELEMENT_TYPE.label('ROOT_TYPE'),
            TParentElement.ELEMENT_TYPE.label('PARENT_TYPE')
        )
        .join(TRootElement, TRootElement.ELEMENT_NO == TElementComponent.ROOT_NO)
        .join(TParentElement, TParentElement.ELEMENT_NO == TElementComponent.PARENT_NO)
        .where(TElementComponent.ELEMENT_NO == element_no)
    )
    return db_execute(stmt).first()


def get_node(element_no):
    """没有子代节点也没有组件节点的就是空间组件"""
    return get_child_node(element_no) or get_component_node(element_no)


def get_element_node(element_no):
    """获取元素节点信息"""
    nodes = localvar__element_nodes.get()
    if nodes == 0:
        nodes = {}
        localvar__element_nodes.set(nodes)
    if element_no in nodes:
        return nodes[element_no]

    entity = get_node(element_no)
    nodes[element_no] = entity
    return entity

def get_root_no(element_no):
    """获取根元素编号"""
    root_no = localvar__root_no.get()
    if root_no == 0:
        node = get_element_node(element_no)
        root_no = node.ROOT_NO if node else None
        if not root_no and is_root_node(element_no):
            root_no = element_no
        localvar__root_no.set(root_no)
    return root_no


def get_worker_no(parent_no):
    stmt = (
        select(
            TElementChildren.ROOT_NO,
            TElementChildren.PARENT_NO,
            TTestElement.ELEMENT_TYPE.label('PARENT_TYPE')
        )
        .join(TTestElement, TTestElement.ELEMENT_NO == TElementChildren.PARENT_NO)
        .where(TElementChildren.ELEMENT_NO == parent_no)
    )
    node = db_execute(stmt).first()
    if node.PARENT_TYPE == ElementType.WORKER.value:
        return node.PARENT_NO
    return get_worker_no(node.PARENT_NO) # 找不到时继续递归往上层找


def get_case_no(element_no):
    """获取用例编号"""
    case_no = localvar__case_no.get()
    if case_no == 0:
        node = get_element_node(element_no)
        if not node or node.ROOT_TYPE == ElementType.SNIPPET.value:
            case_no = None
        elif node.PARENT_TYPE == ElementType.COLLECTION.value:
            case_no = element_no
        else:
            case_no = node.PARENT_NO if node.PARENT_TYPE == ElementType.WORKER.value else get_worker_no(node.PARENT_NO)
        localvar__case_no.set(case_no)
    return case_no


def get_parent_no(element_no):
    """获取父级编号"""
    parents = localvar__parents.get()
    if parents == 0:
        parents = {}
        localvar__parents.set(parents)
    if element_no in parents:
        return parents[element_no]

    node = get_element_node(element_no)
    parent_no = node.PARENT_NO if node else None
    parents[element_no] = parent_no
    return parent_no


@element_created_signal.connect
def record_create_element(sender, root_no, parent_no, element_no):
    case_no = None
    if parent_no:
        parent = test_element_dao.select_by_no(parent_no)
        case_no = parent_no if parent.ELEMENT_TYPE == ElementType.WORKER.value else get_worker_no(parent_no)
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=root_no,
        CASE_NO=case_no,
        PARENT_NO=parent_no,
        ELEMENT_NO=element_no,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.INSERT.value
    )


@element_modified_signal.connect
def record_modify_element(sender, element_no, prop_name=None, attr_name=None, old_value=None, new_value=None):
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=get_root_no(element_no),
        CASE_NO=get_case_no(element_no),
        PARENT_NO=get_parent_no(element_no),
        ELEMENT_NO=element_no,
        PROP_NAME=prop_name,
        ATTR_NAME=attr_name,
        OLD_VALUE=old_value,
        NEW_VALUE=new_value,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.UPDATE.value
    )


@element_removed_signal.connect
def record_remove_element(sender, element_no):
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=get_root_no(element_no),
        CASE_NO=get_case_no(element_no),
        PARENT_NO=get_parent_no(element_no),
        ELEMENT_NO=element_no,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.DELETE.value
    )


@element_moved_signal.connect
def record_move_element(sender, element_no, source_no, source_index, target_no, target_index):
    """不同父级下叫移动"""
    # source_no 为source的父级编号
    # target_no 为target的父级编号
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=get_root_no(source_no),
        CASE_NO=get_case_no(source_no),
        PARENT_NO=source_no,
        ELEMENT_NO=element_no,
        SOURCE_NO=source_no,
        TARGET_NO=target_no,
        SOURCE_INDEX=source_index,
        TARGET_INDEX=target_index,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.MOVE.value
    )


@element_sorted_signal.connect
def record_order_element(sender, element_no, source_index, target_index):
    """相同父级下叫排序"""
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=get_root_no(element_no),
        CASE_NO=get_case_no(element_no),
        PARENT_NO=get_parent_no(element_no),
        ELEMENT_NO=element_no,
        SOURCE_INDEX=source_index,
        TARGET_INDEX=target_index,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.ORDER.value
    )


@element_copied_signal.connect
def record_copy_element(sender, element_no, source_no):
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=get_root_no(element_no),
        CASE_NO=get_case_no(element_no),
        PARENT_NO=get_parent_no(element_no),
        ELEMENT_NO=element_no,
        SOURCE_NO=source_no,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.COPY.value
    )


@element_transferred_signal.connect
def record_transfer_element(sender, collection_no, source_workspace_no, target_workspace_no):
    """集合转移空间"""
    TElementChangelog.insert(
        ROOT_NO=collection_no,
        ELEMENT_NO=collection_no,
        SOURCE_NO=source_workspace_no,
        TARGET_NO=target_workspace_no,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.TRANSFER.value
    )
