#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_service
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from datetime import datetime

from server.common.number_generator import generate_element_no
from server.extensions import db
from server.librarys.decorators.service import http_service
from server.librarys.decorators.transaction import db_transaction
from server.librarys.exception import ServiceError
from server.librarys.helpers.global_helper import Global
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.verify import Verify
from server.script.model import TTestElement, TElementProperty, TElementChildRel
from server.script.services.element_helper import ElementStatus
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_element_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    if req.attr.elementNo:
        conditions.append(TTestElement.element_no == req.attr.elementNo)
    if req.attr.elementName:
        conditions.append(TTestElement.element_name.like(f'%{req.attr.elementName}%'))
    if req.attr.elementComments:
        conditions.append(TTestElement.element_comments.like(f'%{req.attr.elementComments}%'))
    if req.attr.elementType:
        conditions.append(TTestElement.element_type == req.attr.elementType)
    if req.attr.enabled:
        conditions.append(TTestElement.enabled == req.attr.enabled)
    # todo 还有 propertys的条件

    # 列表总数
    total_size = TTestElement.query.filter(*conditions).count()

    # 列表数据
    elements = TTestElement.query.filter(
        *conditions
    ).order_by(
        TTestElement.created_time.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for element in elements:
        data_set.append({
            'elementNo': element.element_no,
            'elementName': element.element_name,
            'elementComments': element.element_comments,
            'elementType': element.element_type,
            'enabled': element.enabled,
            # 'propertys' todo
            # 'childList' todo
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def query_element_all():
    elements = TTestElement.query.order_by(TTestElement.created_time.desc()).all()
    result = []
    for element in elements:
        result.append({
            'elementNo': element.element_no,
            'elementName': element.element_name,
            'elementComments': element.element_comments,
            'elementType': element.element_type,
            'enabled': element.enabled
        })
    return result


@http_service
@db_transaction
def create_element(req: RequestDTO):
    element_no = create_element_no_commit(
        element_name=req.attr.elementName,
        element_comments=req.attr.elementComments,
        element_type=req.attr.elementType,
        propertys=req.attr.propertys,
        child_list=req.attr.childList
    )
    return {'elementNo': element_no}


@http_service
@db_transaction
def modify_element(req: RequestDTO):
    modify_element_no_commit(
        element_no=req.attr.elementNo,
        element_name=req.attr.elementName,
        element_comments=req.attr.elementComments,
        element_type=req.attr.elementType,
        propertys=req.attr.propertys,
        child_list=req.attr.childList
    )
    return None


@http_service
@db_transaction
def delete_element(req: RequestDTO):
    delete_element_no_commit(element_no=req.attr.elementNo)
    return None


@http_service
def enable_element(req: RequestDTO):
    element = TTestElement.query.filter_by(element_no=req.attr.elementNo).first()
    Verify.not_empty(element, '测试元素不存在')

    element.enabled = ElementStatus.ENABLE.value
    element.save()
    return None


@http_service
def disable_element(req: RequestDTO):
    element = TTestElement.query.filter_by(element_no=req.attr.elementNo).first()
    Verify.not_empty(element, '测试元素不存在')

    element.enabled = ElementStatus.DISABLE.value
    element.save()
    return None


@http_service
def add_element_property(req: RequestDTO):
    el_prop = TElementProperty.query.filter_by(
        element_no=req.attr.elementNo,
        property_name=req.attr.propertyName
    ).first()
    Verify.empty(el_prop, '元素属性已存在')

    TElementProperty.create(
        element_no=req.attr.elementNo,
        property_name=req.attr.propertyName,
        property_value=req.attr.propertyValue,
        created_by=Global.operator,
        created_time=datetime.now(),
        updated_by=Global.operator,
        updated_time=datetime.now()
    )
    return None


@http_service
def modify_element_property(req: RequestDTO):
    el_prop = TElementProperty.query.filter_by(
        element_no=req.attr.elementNo,
        property_name=req.attr.propertyName
    ).first()
    Verify.not_empty(el_prop, '元素属性不存在')

    el_prop.property_value = req.attr.propertyValue
    el_prop.save()
    return None


@http_service
def remove_element_property(req: RequestDTO):
    el_prop = TElementProperty.query.filter_by(
        element_no=req.attr.elementNo,
        property_name=req.attr.propertyName
    ).first()
    Verify.not_empty(el_prop, '元素属性不存在')
    el_prop.delete()
    return None


@http_service
@db_transaction
def add_element_child(req: RequestDTO):
    add_element_child_no_commit(
        parent_no=req.attr.parentNo,
        child_list=req.attr.childList
    )
    return None


@http_service
@db_transaction
def modify_element_child(req: RequestDTO):
    modify_element_child_no_commit(
        parent_no=req.attr.parentNo,
        child_list=req.attr.childList
    )


@http_service
def modify_element_child_order(req: RequestDTO):
    el_child = TElementChildRel.query.filter_by(
        parent_no=req.attr.parentNo,
        child_no=req.attr.childNo
    ).first()
    Verify.not_empty(el_child, '子元素不存在')

    el_child.child_order = req.attr.childOrder
    el_child.save()
    return None


def create_element_no_commit(element_name, element_comments, element_type,
                             propertys: dict = None,
                             child_list: [dict] = None):
    element_no = generate_element_no()

    TTestElement.create(
        commit=False,
        element_no=element_no,
        element_name=element_name,
        element_comments=element_comments,
        element_type=element_type,
        enabled=ElementStatus.ENABLE.value,
        created_by=Global.operator,
        created_time=datetime.now(),
        updated_by=Global.operator,
        updated_time=datetime.now()
    )
    db.session.flush()

    if propertys:
        add_element_property_no_commit(element_no, propertys)
    if child_list:
        add_element_child_no_commit(element_no, child_list)

    return element_no


def add_element_property_no_commit(element_no, propertys: dict):
    for prop_name, prop_value in propertys.items():
        TElementProperty.create(
            commit=False,
            element_no=element_no,
            property_name=prop_name,
            property_value=prop_value,
            created_by=Global.operator,
            created_time=datetime.now(),
            updated_by=Global.operator,
            updated_time=datetime.now()
        )

    db.session.flush()


def add_element_child_no_commit(parent_no, child_list: [dict]):
    for child in child_list:
        child_no = create_element_no_commit(
            element_name=child.get('elementName'),
            element_comments=child.get('elementComments'),
            element_type=child.get('elementType'),
            propertys=child.get('propertys'),
            child_list=child.get('childList')
        )
        TElementChildRel.create(
            commit=False,
            parent_no=parent_no,
            child_no=child_no,
            child_order=child.get('order'),
            created_by=Global.operator,
            created_time=datetime.now(),
            updated_by=Global.operator,
            updated_time=datetime.now()
        )

    db.session.flush()


def modify_element_no_commit(element_no, element_name, element_comments, element_type, propertys, child_list):
    element = TTestElement.query.filter_by(element_no=element_no).first()
    Verify.not_empty(element, '测试元素不存在')

    if element_name is not None:
        element.element_name = element_name
    if element_comments is not None:
        element.element_comments = element_comments
    if element_type is not None:
        element.element_type = element_type

    element.save(commit=False)
    db.session.flush()

    if propertys is not None:
        modify_element_property_no_commit(element_no, propertys)
    if child_list is not None:
        modify_element_child_no_commit(element_no, child_list)


def modify_element_property_no_commit(element_no, propertys: dict):
    for prop_name, prop_value in propertys:
        el_prop = TElementProperty.query.filter_by(element_no=element_no, property_name=prop_name).first()
        el_prop.property_value = prop_value
        el_prop.save(commit=False)

    db.session.flush()


def modify_element_child_no_commit(parent_no, child_list: [dict]):
    for child in child_list:
        if 'elementNo' not in child:
            raise ServiceError('子代元素编号不能为空')

        modify_element_no_commit(
            element_no=child.get('elementNo'),
            element_name=child.get('elementName'),
            element_comments=child.get('elementComments'),
            element_type=child.get('elementType'),
            propertys=child.get('propertys'),
            child_list=child.get('childList')
        )

        modify_element_child_order_no_commit(
            parent_no=parent_no,
            child_no=child.get('elementNo'),
            child_order=child.get('order')
        )


def modify_element_child_order_no_commit(parent_no, child_no, child_order):
    if child_order is not None:
        element = TElementChildRel.query.filter_by(parent_no=parent_no, child_no=child_no).first()
        element.child_order = child_order

        element.save(commit=False)
        db.session.flush()


def delete_element_no_commit(element_no):
    element = TTestElement.query.filter_by(element_no=element_no).first()
    Verify.not_empty(element, '测试元素不存在')

    el_childs = TElementChildRel.query.filter_by(element_no=element.element_no).all()
    for el_child in el_childs:
        child = TTestElement.query.filter_by(element_no=el_child.element_no).first()
        child.delete(commit=False)
    element.delete(commit=False)

    db.session.flush()
