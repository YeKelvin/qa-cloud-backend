#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_service
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.decorators.transaction import db_transaction
from app.common.request import RequestDTO
from app.common.validator import assert_blank
from app.common.validator import assert_not_blank
from app.extension import db
from app.script.enums import ElementStatus
from app.script.models import TElementChildRel
from app.script.models import TElementProperty
from app.script.models import TTestElement
from app.script.models import TWorkspace
from app.script.models import TWorkspaceCollectionRel
from app.script.services import element_helper as helper
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_element_list(req: RequestDTO):
    # 查询条件
    conditions = [TTestElement.DEL_STATE == 0]

    if req.attr.elementNo:
        conditions.append(TTestElement.ELEMENT_NO == req.attr.elementNo)
    if req.attr.elementName:
        conditions.append(TTestElement.ELEMENT_NAME.like(f'%{req.attr.elementName}%'))
    if req.attr.elementComments:
        conditions.append(TTestElement.ELEMENT_COMMENTS.like(f'%{req.attr.elementComments}%'))
    if req.attr.elementType:
        conditions.append(TTestElement.ELEMENT_TYPE.like(f'%{req.attr.elementType}%'))
    if req.attr.enabled:
        conditions.append(TTestElement.ENABLED.like(f'%{req.attr.enabled}%'))

    if req.attr.workspaceNo:
        conditions.append(TWorkspaceCollectionRel.DEL_STATE == 0)
        conditions.append(TWorkspaceCollectionRel.COLLECTION_NO == TTestElement.ELEMENT_NO)
        conditions.append(TWorkspaceCollectionRel.WORKSPACE_NO.like(f'%{req.attr.workspaceNo}%'))
    if req.attr.workspaceName:
        conditions.append(TWorkspace.DEL_STATE == 0)
        conditions.append(TWorkspaceCollectionRel.DEL_STATE == 0)
        conditions.append(TWorkspaceCollectionRel.COLLECTION_NO == TTestElement.ELEMENT_NO)
        conditions.append(TWorkspaceCollectionRel.WORKSPACE_NO == TWorkspace.WORKSPACE_NO)
        conditions.append(TWorkspace.WORKSPACE_NAME.like(f'%{req.attr.workspaceName}%'))

    pagination = db.session.query(
        TTestElement.ELEMENT_NO,
        TTestElement.ELEMENT_NAME,
        TTestElement.ELEMENT_COMMENTS,
        TTestElement.ELEMENT_TYPE,
        TTestElement.ENABLED
    ).filter(*conditions).order_by(TTestElement.CREATED_TIME.desc()).paginate(req.attr.page, req.attr.pageSize)

    # 组装数据
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
def query_element_all(req: RequestDTO):
    # 查询条件
    conditions = [
        TTestElement.DEL_STATE == 0,
        TWorkspaceCollectionRel.DEL_STATE == 0,
        TWorkspaceCollectionRel.COLLECTION_NO == TTestElement.ELEMENT_NO
    ]

    if req.attr.workspaceNo:
        conditions.append(TWorkspaceCollectionRel.WORKSPACE_NO.like(f'%{req.attr.workspaceNo}%'))
    if req.attr.elementType:
        conditions.append(TTestElement.ELEMENT_TYPE.like(f'%{req.attr.elementType}%'))
    if req.attr.enabled:
        conditions.append(TTestElement.ENABLED.like(f'%{req.attr.enabled}%'))

    items = db.session.query(
        TTestElement.ELEMENT_NO,
        TTestElement.ELEMENT_NAME,
        TTestElement.ELEMENT_COMMENTS,
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
def query_element_info(req: RequestDTO):
    element = TTestElement.query_by(ELEMENT_NO=req.attr.elementNo).first()
    assert_not_blank(element, '测试元素不存在')

    el_props = TElementProperty.query_by(ELEMENT_NO=req.attr.elementNo).all()
    has_children = TElementChildRel.query_by(PARENT_NO=req.attr.elementNo).count() > 0
    propertys = {}
    for prop in el_props:
        propertys[prop.PROPERTY_NAME] = prop.PROPERTY_VALUE

    return {
        'elementNo': element.ELEMENT_NO,
        'elementName': element.ELEMENT_NAME,
        'elementComments': element.ELEMENT_COMMENTS,
        'elementType': element.ELEMENT_TYPE,
        'enabled': element.ENABLED,
        'propertys': propertys,
        'hasChildren': has_children
    }


@http_service
def query_element_children(req: RequestDTO):
    return helper.depth_query_element_children(req.attr.elementNo, req.attr.depth)


@http_service
@db_transaction
def create_element(req: RequestDTO):
    element_no = helper.create_element(
        element_name=req.attr.elementName,
        element_comments=req.attr.elementComments,
        element_type=req.attr.elementType,
        element_class=req.attr.elementClass,
        propertys=req.attr.propertys,
        children=req.attr.children
    )

    if req.attr.workspaceNo:
        workspace = TWorkspace.query_by(WORKSPACE_NO=req.attr.workspaceNo).first()
        assert_not_blank(workspace, '测试项目不存在')

        TWorkspaceCollectionRel.create(
            commit=False,
            WORKSPACE_NO=req.attr.workspaceNo,
            COLLECTION_NO=element_no
        )

    return {'elementNo': element_no}


@http_service
@db_transaction
def modify_element(req: RequestDTO):
    helper.modify_element(
        element_no=req.attr.elementNo,
        element_name=req.attr.elementName,
        element_comments=req.attr.elementComments,
        propertys=req.attr.propertys,
        children=req.attr.children
    )
    return None


@http_service
@db_transaction
def delete_element(req: RequestDTO):
    return helper.delete_element(element_no=req.attr.elementNo)


@http_service
def enable_element(req: RequestDTO):
    element = TTestElement.query_by(ELEMENT_NO=req.attr.elementNo).first()
    assert_not_blank(element, '测试元素不存在')

    element.enabled = ElementStatus.ENABLE.value
    element.save()
    return None


@http_service
def disable_element(req: RequestDTO):
    element = TTestElement.query_by(ELEMENT_NO=req.attr.elementNo).first()
    assert_not_blank(element, '测试元素不存在')

    element.enabled = ElementStatus.DISABLE.value
    element.save()
    return None


@http_service
def add_element_property(req: RequestDTO):
    el_prop = TElementProperty.query_by(ELEMENT_NO=req.attr.elementNo, PROPERTY_NAME=req.attr.propertyName).first()
    assert_blank(el_prop, '元素属性已存在')

    TElementProperty.create(
        ELEMENT_NO=req.attr.elementNo,
        PROPERTY_NAME=req.attr.propertyName,
        PROPERTY_VALUE=req.attr.propertyValue
    )
    return None


@http_service
def modify_element_property(req: RequestDTO):
    el_prop = TElementProperty.query_by(ELEMENT_NO=req.attr.elementNo, PROPERTY_NAME=req.attr.propertyName).first()
    assert_not_blank(el_prop, '元素属性不存在')

    el_prop.property_value = req.attr.propertyValue
    el_prop.save()
    return None


@http_service
@db_transaction
def add_element_children(req: RequestDTO):
    helper.add_element_child(
        parent_no=req.attr.parentNo,
        children=req.attr.children
    )
    return None


@http_service
@db_transaction
def modify_element_children(req: RequestDTO):
    helper.modify_element_child(children=req.attr.children)


@http_service
def move_up_child_order(req: RequestDTO):
    child_rel = TElementChildRel.query_by(PARENT_NO=req.attr.parentNo, CHILD_NO=req.attr.childNo).first()
    assert_not_blank(child_rel, '子元素不存在')

    children_length = TElementChildRel.query_by(PARENT_NO=req.attr.parentNo).count()
    child_current_order = child_rel.CHILD_ORDER
    if children_length == 1 or child_current_order == 1:
        return None

    upper_child_rel = TElementChildRel.query_by(
        PARENT_NO=req.attr.parentNo,
        CHILD_ORDER=child_current_order - 1
    ).first()
    upper_child_rel.update(CHILD_ORDER=upper_child_rel.CHILD_ORDER + 1)
    child_rel.update(CHILD_ORDER=child_rel.CHILD_ORDER - 1)

    return None


@http_service
def move_down_child_order(req: RequestDTO):
    child_rel = TElementChildRel.query_by(PARENT_NO=req.attr.parentNo, CHILD_NO=req.attr.childNo).first()
    assert_not_blank(child_rel, '子元素不存在')

    children_length = TElementChildRel.query_by(PARENT_NO=req.attr.parentNo).count()
    current_child_order = child_rel.CHILD_ORDER
    if children_length == current_child_order:
        return None

    lower_child_rel = TElementChildRel.query_by(
        PARENT_NO=req.attr.parentNo,
        CHILD_ORDER=current_child_order + 1,
    ).first()
    lower_child_rel.update(CHILD_ORDER=lower_child_rel.CHILD_ORDER - 1)
    child_rel.update(CHILD_ORDER=child_rel.CHILD_ORDER + 1)

    return None


@http_service
def duplicate_element(req: RequestDTO):
    element = TTestElement.query_by(ELEMENT_NO=req.attr.element_no).first()
    assert_not_blank(element, '测试元素不存在')

    # todo 复制元素
    return None
