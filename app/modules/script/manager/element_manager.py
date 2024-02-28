#!/usr/bin python3
# @File    : element_manager.py
# @Time    : 2023-05-16 17:41:28
# @Author  : Kelvin.Ye
from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.database import db_execute
from app.modules.script.dao import element_children_dao
from app.modules.script.dao import element_property_dao
from app.modules.script.dao import test_element_dao
from app.modules.script.enum import ElementType
from app.modules.script.model import TElementChildren
from app.modules.script.model import TTestElement
from app.tools.exceptions import ServiceError
from app.utils.json_util import from_json


TRootElement: TTestElement = aliased(TTestElement)
TParentElement: TTestElement = aliased(TTestElement)
TChildElement: TTestElement = aliased(TTestElement)


def get_workspace_no(root_no) -> str:
    """获取元素空间编号"""
    root = test_element_dao.get_root_by_number(root_no)
    if not root:
        raise ServiceError(msg='根元素不存在')
    if not root.WORKSPACE_NO:
        raise ServiceError(msg='根元素没有绑定空间')
    return root.WORKSPACE_NO


def get_root_no(element_no) -> str:
    """根据元素编号获取根元素编号"""
    # 没有节点的就是根元素或者空间元素
    if not (node := element_children_dao.select_by_child(element_no)):
        return element_no
    if not node.ROOT_NO:
        raise ServiceError(msg=f'元素编号:[ {element_no} ] 根元素编号为空')
    return node.ROOT_NO


def get_element_node(element_no):
    stmt = (
        select(
            TElementChildren.ROOT_NO,
            TElementChildren.PARENT_NO,
            TRootElement.ELEMENT_TYPE.label('ROOT_TYPE'),
            TParentElement.ELEMENT_TYPE.label('PARENT_TYPE')
        )
        .outerjoin(TRootElement, TRootElement.ELEMENT_NO == TElementChildren.ROOT_NO)
        .outerjoin(TParentElement, TParentElement.ELEMENT_NO == TElementChildren.PARENT_NO)
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
        raise ServiceError(msg='查找用例编号失败')


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


def get_element_children_node(parent_no):
    """根据父级查询所有子代节点和子代类型"""
    stmt = (
        select(
            TElementChildren.ROOT_NO,
            TElementChildren.PARENT_NO,
            TElementChildren.ELEMENT_NO,
            TElementChildren.ELEMENT_SORT,
            TRootElement.ELEMENT_TYPE.label('ROOT_TYPE'),
            TRootElement.ELEMENT_CLASS.label('ROOT_CLASS'),
            TParentElement.ELEMENT_TYPE.label('PARENT_TYPE'),
            TParentElement.ELEMENT_CLASS.label('PARENT_CLASS'),
            TChildElement.ELEMENT_TYPE.label('CHILD_TYPE'),
            TChildElement.ELEMENT_CLASS.label('CHILD_CLASS')
        )
        .outerjoin(TRootElement, TRootElement.ELEMENT_NO == TElementChildren.ROOT_NO)
        .outerjoin(TParentElement, TParentElement.ELEMENT_NO == TElementChildren.PARENT_NO)
        .outerjoin(TChildElement, TChildElement.ELEMENT_NO == TElementChildren.ELEMENT_NO)
        .where(
            TChildElement.DELETED == 0,
            TParentElement.DELETED == 0,
            TElementChildren.DELETED == 0,
            TElementChildren.PARENT_NO == parent_no
        )
    )
    return db_execute(stmt.order_by(TElementChildren.ELEMENT_SORT)).all()
