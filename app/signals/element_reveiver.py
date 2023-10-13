#!/usr/bin python3
# @File    : element_reveiver.py
# @Time    : 2023-09-26 16:27:14
# @Author  : Kelvin.Ye
from contextvars import ContextVar

from flask import request

from app.modules.script.dao import element_children_dao
from app.modules.script.enum import ElementOperationType
from app.modules.script.model import TElementChangelog
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


localvar__element_nodes = ContextVar('ELEMENT_NODES', default={})
localvar__parent_no = ContextVar('PARENT_NO', default=None)
localvar__root_no = ContextVar('ROOT_NO', default=None)



def get_workspace_no():
    """获取当前空间编号"""
    if workspace_no := request.headers.get('x-workspace-no'):
        return workspace_no
    else:
        raise ServiceError('获取空间编号失败')


def get_element_node(element_no):
    """获取元素节点信息"""
    nodes = localvar__element_nodes.get()
    if element_no in nodes:
        return nodes[element_no]

    entity = element_children_dao.select_by_child(element_no)
    if not entity:
        raise ServiceError('元素节点不存在')
    node = {'root_no': entity.ROOT_NO, 'parent_no': entity.PARENT_NO}
    nodes[element_no] = node
    return node

def get_root_no(element_no):
    """获取根元素编号"""
    root_no = localvar__root_no.get()
    if not root_no:
        root_no = get_element_node(element_no)['root_no']
        localvar__root_no.set(root_no)
    return root_no


def get_parent_no(element_no):
    """获取父级编号"""
    parent_no = localvar__parent_no.get()
    if not parent_no:
        parent_no = get_element_node(element_no)['parent_no']
        localvar__parent_no.set(parent_no)
    return parent_no


@element_created_signal.connect
def record_create_element(sender, root_no, parent_no, element_no):
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=root_no,
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
    node = element_children_dao.select_by_child(element_no)
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=node.ROOT_NO,
        PARENT_NO=node.PARENT_NO,
        ELEMENT_NO=element_no,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.DELETE.value
    )


@element_moved_signal.connect
def record_move_element(sender, source_no, target_no):
    """不同父级下叫移动"""
    node = element_children_dao.select_by_child(source_no)
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=node.ROOT_NO,
        PARENT_NO=node.PARENT_NO,
        ELEMENT_NO=source_no,
        SOURCE_NO=source_no,
        TARGET_NO=target_no, # target的父级
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.MOVE.value
    )


@element_sorted_signal.connect
def record_order_element(sender, element_no, source_index, target_index):
    """相同父级下叫排序"""
    node = element_children_dao.select_by_child(element_no)
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=node.ROOT_NO,
        PARENT_NO=node.PARENT_NO,
        ELEMENT_NO=element_no,
        SOURCE_INDEX=source_index,
        TARGET_INDEX=target_index,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.ORDER.value
    )


@element_copied_signal.connect
def record_copy_element(sender, element_no, source_no):
    node = element_children_dao.select_by_child(element_no)
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=node.ROOT_NO,
        PARENT_NO=node.PARENT_NO,
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
