#!/usr/bin python3
# @File    : element_manager.py
# @Time    : 2023-05-16 17:41:28
# @Author  : Kelvin.Ye
from sqlalchemy import select

from app.database import db_execute
from app.modules.script.dao import element_children_dao
from app.modules.script.dao import element_property_dao
from app.modules.script.dao import workspace_script_dao
from app.modules.script.enum import ElementType
from app.modules.script.model import TElementChildren
from app.modules.script.model import TTestElement
from app.tools.exceptions import ServiceError
from app.utils.json_util import from_json


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


def get_element_node(element_no):
    stmt = (
        select(
            TElementChildren.ROOT_NO,
            TElementChildren.PARENT_NO,
            TTestElement.ELEMENT_TYPE.label('PARENT_TYPE')
        )
        .join(TTestElement, TTestElement.ELEMENT_NO == TElementChildren.PARENT_NO)
        .where(TElementChildren.ELEMENT_NO == element_no)
    )
    return db_execute(stmt).first()


def get_case_no(element_no) -> str:
    if node := get_element_node(element_no):
        return (
            node.PARENT_NO
            if node.PARENT_TYPE == ElementType.WORKER.value
            else get_case_no(node.PARENT_NO)
        )
    else:
        raise ServiceError('查找用例编号失败')


def get_element_property(element_no):
    # 查询元素属性，只查询 enabled 的属性
    props = element_property_dao.select_all_enabled(element_no)

    properties = {}
    for prop in props:
        if prop.PROPERTY_TYPE == 'STR':
            properties[prop.PROPERTY_NAME] = prop.PROPERTY_VALUE
            continue
        if prop.PROPERTY_TYPE == 'DICT':
            properties[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
            continue
        if prop.PROPERTY_TYPE == 'LIST':
            properties[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
            continue

    return properties
