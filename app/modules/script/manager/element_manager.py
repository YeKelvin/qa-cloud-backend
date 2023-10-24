#!/usr/bin python3
# @File    : element_manager.py
# @Time    : 2023-05-16 17:41:28
# @Author  : Kelvin.Ye
from app.modules.script.dao import element_children_dao
from app.modules.script.dao import workspace_script_dao
from app.tools.exceptions import ServiceError


def get_workspace_no(collection_no) -> str:
    """获取元素空间编号"""
    if workspace_script := workspace_script_dao.select_by_script(collection_no):
        return workspace_script.WORKSPACE_NO
    else:
        raise ServiceError('查询元素空间失败')


def get_root_no(element_no) -> str:
    """根据元素编号获取根元素编号"""
    if not (node := element_children_dao.select_by_child(element_no)):
        return element_no
    if not node.ROOT_NO:
        raise ServiceError(f'元素编号:[ {element_no} ] 根元素编号为空')
    return node.ROOT_NO


def get_case_no(element_no) -> str:
    ...
