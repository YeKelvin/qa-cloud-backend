#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_service.py
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.extension import db
from app.script.enum import ElementStatus
from app.script.model import TElementChildRel
from app.script.model import TElementProperty
from app.script.model import TTestElement
from app.script.model import TWorkspaceCollectionRel
from app.script.service import element_helper as helper
from app.system.model import TWorkspace
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_element_list(req):
    # 查询条件
    conditions = [TTestElement.DEL_STATE == 0]

    if req.elementNo:
        conditions.append(TTestElement.ELEMENT_NO == req.elementNo)
    if req.elementName:
        conditions.append(TTestElement.ELEMENT_NAME.like(f'%{req.elementName}%'))
    if req.elementRemark:
        conditions.append(TTestElement.ELEMENT_REMARK.like(f'%{req.elementRemark}%'))
    if req.elementType:
        conditions.append(TTestElement.ELEMENT_TYPE.like(f'%{req.elementType}%'))
    if req.enabled:
        conditions.append(TTestElement.ENABLED.like(f'%{req.enabled}%'))

    if req.workspaceNo:
        conditions.append(TWorkspaceCollectionRel.DEL_STATE == 0)
        conditions.append(TWorkspaceCollectionRel.COLLECTION_NO == TTestElement.ELEMENT_NO)
        conditions.append(TWorkspaceCollectionRel.WORKSPACE_NO.like(f'%{req.workspaceNo}%'))
    if req.workspaceName:
        conditions.append(TWorkspace.DEL_STATE == 0)
        conditions.append(TWorkspaceCollectionRel.DEL_STATE == 0)
        conditions.append(TWorkspaceCollectionRel.COLLECTION_NO == TTestElement.ELEMENT_NO)
        conditions.append(TWorkspaceCollectionRel.WORKSPACE_NO == TWorkspace.WORKSPACE_NO)
        conditions.append(TWorkspace.WORKSPACE_NAME.like(f'%{req.workspaceName}%'))

    pagination = db.session.query(
        TTestElement.ELEMENT_NO,
        TTestElement.ELEMENT_NAME,
        TTestElement.ELEMENT_REMARK,
        TTestElement.ELEMENT_TYPE,
        TTestElement.ENABLED
    ).filter(*conditions).order_by(TTestElement.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data_set = []
    for item in pagination.items:
        data_set.append({
            'elementNo': item.ELEMENT_NO,
            'elementName': item.ELEMENT_NAME,
            'elementType': item.ELEMENT_TYPE,
            'enabled': item.ENABLED
        })
    return {'dataSet': data_set, 'totalSize': pagination.total}


@http_service
def query_element_all(req):
    # 查询条件
    conditions = [
        TTestElement.DEL_STATE == 0,
        TWorkspaceCollectionRel.DEL_STATE == 0,
        TWorkspaceCollectionRel.COLLECTION_NO == TTestElement.ELEMENT_NO
    ]

    if req.workspaceNo:
        conditions.append(TWorkspaceCollectionRel.WORKSPACE_NO.like(f'%{req.workspaceNo}%'))
    if req.elementType:
        conditions.append(TTestElement.ELEMENT_TYPE.like(f'%{req.elementType}%'))
    if req.enabled:
        conditions.append(TTestElement.ENABLED.like(f'%{req.enabled}%'))

    items = db.session.query(
        TTestElement.ELEMENT_NO,
        TTestElement.ELEMENT_NAME,
        TTestElement.ELEMENT_REMARK,
        TTestElement.ELEMENT_TYPE,
        TTestElement.ENABLED
    ).filter(*conditions).order_by(TTestElement.CREATED_TIME.desc()).all()

    result = []
    for item in items:
        result.append({
            'elementNo': item.ELEMENT_NO,
            'elementName': item.ELEMENT_NAME,
            'elementType': item.ELEMENT_TYPE,
            'enabled': item.ENABLED
        })
    return result


@http_service
def query_element_info(req):
    element = TTestElement.query_by(ELEMENT_NO=req.elementNo).first()
    check_is_not_blank(element, '测试元素不存在')

    el_props = TElementProperty.query_by(ELEMENT_NO=req.elementNo).all()
    has_children = TElementChildRel.query_by(PARENT_NO=req.elementNo).count() > 0
    propertys = {}
    for prop in el_props:
        propertys[prop.PROPERTY_NAME] = prop.PROPERTY_VALUE

    return {
        'elementNo': element.ELEMENT_NO,
        'elementName': element.ELEMENT_NAME,
        'elementRemark': element.ELEMENT_REMARK,
        'elementType': element.ELEMENT_TYPE,
        'enabled': element.ENABLED,
        'propertys': propertys,
        'hasChildren': has_children
    }


@http_service
def query_element_children(req):
    return helper.depth_query_element_children(req.elementNo, req.depth)


@http_service
@transactional
def create_element(req):
    element_no = helper.create_element(
        element_name=req.elementName,
        element_remark=req.elementRemark,
        element_type=req.elementType,
        element_class=req.elementClass,
        propertys=req.propertys,
        children=req.children
    )

    if req.workspaceNo:
        workspace = TWorkspace.query_by(WORKSPACE_NO=req.workspaceNo).first()
        check_is_not_blank(workspace, '测试项目不存在')

        TWorkspaceCollectionRel.insert(
            WORKSPACE_NO=req.workspaceNo,
            COLLECTION_NO=element_no
        )

    return {'elementNo': element_no}


@http_service
@transactional
def modify_element(req):
    helper.modify_element(
        element_no=req.elementNo,
        element_name=req.elementName,
        element_remark=req.elementRemark,
        propertys=req.propertys,
        children=req.children
    )
    return None


@http_service
@transactional
def delete_element(req):
    return helper.delete_element(element_no=req.elementNo)


@http_service
def enable_element(req):
    element = TTestElement.query_by(ELEMENT_NO=req.elementNo).first()
    check_is_not_blank(element, '测试元素不存在')

    element.enabled = ElementStatus.ENABLE.value
    element.submit()
    return None


@http_service
def disable_element(req):
    element = TTestElement.query_by(ELEMENT_NO=req.elementNo).first()
    check_is_not_blank(element, '测试元素不存在')

    element.enabled = ElementStatus.DISABLE.value
    element.submit()
    return None


@http_service
def add_element_property(req):
    el_prop = TElementProperty.query_by(ELEMENT_NO=req.elementNo, PROPERTY_NAME=req.propertyName).first()
    check_is_blank(el_prop, '元素属性已存在')

    TElementProperty.insert(
        ELEMENT_NO=req.elementNo,
        PROPERTY_NAME=req.propertyName,
        PROPERTY_VALUE=req.propertyValue
    )
    return None


@http_service
def modify_element_property(req):
    el_prop = TElementProperty.query_by(ELEMENT_NO=req.elementNo, PROPERTY_NAME=req.propertyName).first()
    check_is_not_blank(el_prop, '元素属性不存在')

    el_prop.property_value = req.propertyValue
    el_prop.submit()
    return None


@http_service
@transactional
def add_element_children(req):
    helper.add_element_child(
        parent_no=req.parentNo,
        children=req.children
    )
    return None


@http_service
@transactional
def modify_element_children(req):
    helper.modify_element_child(children=req.children)


@http_service
def move_up_child_order(req):
    child_rel = TElementChildRel.query_by(PARENT_NO=req.parentNo, CHILD_NO=req.childNo).first()
    check_is_not_blank(child_rel, '子元素不存在')

    children_length = TElementChildRel.query_by(PARENT_NO=req.parentNo).count()
    child_current_order = child_rel.CHILD_ORDER
    if children_length == 1 or child_current_order == 1:
        return None

    upper_child_rel = TElementChildRel.query_by(
        PARENT_NO=req.parentNo,
        CHILD_ORDER=child_current_order - 1
    ).first()
    upper_child_rel.update(CHILD_ORDER=upper_child_rel.CHILD_ORDER + 1)
    child_rel.update(CHILD_ORDER=child_rel.CHILD_ORDER - 1)

    return None


@http_service
def move_down_child_order(req):
    child_rel = TElementChildRel.query_by(PARENT_NO=req.parentNo, CHILD_NO=req.childNo).first()
    check_is_not_blank(child_rel, '子元素不存在')

    children_length = TElementChildRel.query_by(PARENT_NO=req.parentNo).count()
    current_child_order = child_rel.CHILD_ORDER
    if children_length == current_child_order:
        return None

    lower_child_rel = TElementChildRel.query_by(
        PARENT_NO=req.parentNo,
        CHILD_ORDER=current_child_order + 1,
    ).first()
    lower_child_rel.update(CHILD_ORDER=lower_child_rel.CHILD_ORDER - 1)
    child_rel.update(CHILD_ORDER=child_rel.CHILD_ORDER + 1)

    return None


@http_service
def duplicate_element(req):
    element = TTestElement.query_by(ELEMENT_NO=req.element_no).first()
    check_is_not_blank(element, '测试元素不存在')

    # todo 复制元素
    return None
