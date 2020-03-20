#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_service
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from datetime import datetime

from server.common.number_generator import generate_element_no, generate_property_no
from server.extensions import db
from server.librarys.decorators.service import http_service
from server.librarys.decorators.transaction import db_transaction
from server.librarys.helpers.global_helper import Global
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.verify import Verify
from server.script.model import TTestElement, TElementProperty, TElementPropertyRel, TElementChildRel
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
        element_propertys=req.attr.propertys,
        element_child_list=req.attr.childList
    )
    return {'element_no': element_no}


@http_service
def modify_element(req: RequestDTO):
    element = TTestElement.query.filter_by(element_no=req.attr.elementNo).first()
    Verify.not_empty(element, '测试元素不存在')

    if req.attr.elementName is not None:
        element.element_name = req.attr.elementName
    if req.attr.elementComments is not None:
        element.element_comments = req.attr.elementComments

    element.save()
    return None


@http_service
def delete_element(req: RequestDTO):
    element = TTestElement.query.filter_by(element_no=req.attr.elementNo).first()
    Verify.not_empty(element, '测试元素不存在')

    element.delete()
    return None


@http_service
def add_element_property(req: RequestDTO):
    pass


@http_service
def modify_element_property(req: RequestDTO):
    pass


@http_service
def remove_element_property(req: RequestDTO):
    pass


@http_service
def add_element_child(req: RequestDTO):
    pass


@http_service
def modify_element_child(req: RequestDTO):
    pass


@http_service
def remove_element_child():
    pass


def create_element_no_commit(element_name, element_comments, element_type, element_propertys: dict,
                             element_child_list: [dict]):
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

    if element_propertys:
        add_element_property_no_commit(element_no, element_propertys)
    if element_child_list:
        add_element_child_no_commit(element_no, element_child_list)

    return element_no


def add_element_property_no_commit(element_no, element_property: dict):
    for prop_name, prop_value in element_property.items():
        property_no = generate_property_no()
        TElementProperty.create(
            commit=False,
            property_no=property_no,
            property_name=prop_name,
            property_value=prop_value,
            created_by=Global.operator,
            created_time=datetime.now(),
            updated_by=Global.operator,
            updated_time=datetime.now()
        )
        TElementPropertyRel.create(
            commit=False,
            element_no=element_no,
            property_no=property_no,
            created_by=Global.operator,
            created_time=datetime.now(),
            updated_by=Global.operator,
            updated_time=datetime.now()
        )
    db.session.flush()


def add_element_child_no_commit(element_no, child_list: [dict]):
    for child in child_list:
        child_no = create_element_no_commit(**child)
        TElementChildRel.create(
            commit=False,
            element_no=element_no,
            child_order='',
            child_no=child_no,
            created_by=Global.operator,
            created_time=datetime.now(),
            updated_by=Global.operator,
            updated_time=datetime.now()
        )
    db.session.flush()
