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
from server.script.model import TTestElement, TElementProperty, TElementChildRel, TItemCollectionRel, TTestItem
from server.script.services.element_helper import ElementStatus
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_element_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    if req.attr.itemNo:
        conditions.append(TItemCollectionRel.item_no == req.attr.itemNo)
    if req.attr.itemName:
        conditions.append(TTestItem.item_name.like(f'%{req.attr.itemName}%'))
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

    # 列表总数，列表数据
    if req.attr.itemName:
        total_size, elements = select_item_and_collection_rel_and_element(conditions, offset, limit)
    elif req.attr.itemNo:
        total_size, elements = select_item_collection_rel_and_element(conditions, offset, limit)
    else:
        total_size, elements = select_element(conditions, offset, limit)

    # 组装响应数据
    data_set = []
    for element in elements:
        data_set.append({
            'elementNo': element.element_no,
            'elementName': element.element_name,
            'elementComments': element.element_comments,
            'elementType': element.element_type,
            'enabled': element.enabled
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def query_element_all(req: RequestDTO):
    # 查询条件
    conditions = []

    if req.attr.itemNo:
        conditions.append(TItemCollectionRel.item_no == req.attr.itemNo)
    if req.attr.elementType:
        conditions.append(TTestElement.element_type == req.attr.elementType)
    if req.attr.enabled:
        conditions.append(TTestElement.enabled == req.attr.enabled)

    elements = TTestElement.query.join(
        TItemCollectionRel, TItemCollectionRel.collection_no == TTestElement.element_no
    ).filter(
        *conditions
    ).order_by(
        TTestElement.created_time.desc()
    ).all()
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
def query_element_info(req: RequestDTO):
    element = TTestElement.query.filter_by(element_no=req.attr.elementNo).first()
    Verify.not_empty(element, '测试元素不存在')

    el_props = TElementProperty.query.filter_by(element_no=req.attr.elementNo).all()
    propertys = {}
    for prop in el_props:
        propertys[prop.property_name] = prop.property_value

    return {
        'elementNo': element.element_no,
        'elementName': element.element_name,
        'elementComments': element.element_comments,
        'elementType': element.element_type,
        'enabled': element.enabled,
        'propertys': propertys
    }


@http_service
def query_element_child(req: RequestDTO):
    child_rels = TElementChildRel.query.filter_by(parent_no=req.attr.elementNo).all()
    # 根据 child_order排序
    child_rels.sort(key=lambda k: k.child_order)
    result = []
    for child_rel in child_rels:
        conditions = [TTestElement.element_no == child_rel.child_no]
        if req.attr.elementType:
            conditions.append(TTestElement.element_type == req.attr.elementType)
        element = TTestElement.query.filter(*conditions).first()
        if element:
            result.append({
                'elementNo': element.element_no,
                'elementName': element.element_name,
                'elementComments': element.element_comments,
                'elementType': element.element_type,
                'enabled': element.enabled,
                'childOrder': child_rel.child_order
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

    if req.attr.itemNo:
        item = TTestItem.query.filter_by(item_no=req.attr.itemNo).first()
        Verify.not_empty(item, '测试项目不存在')

        TItemCollectionRel.create(
            commit=False,
            item_no=item.item_no,
            collection_no=element_no
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
    return delete_element_no_commit(element_no=req.attr.elementNo)


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
    modify_element_child_no_commit(child_list=req.attr.childList)


@http_service
def move_up_element_child_order(req: RequestDTO):
    child_rel = TElementChildRel.query.filter_by(
        parent_no=req.attr.parentNo,
        child_no=req.attr.childNo
    ).first()
    Verify.not_empty(child_rel, '子元素不存在')

    childs_length = TElementChildRel.query.filter_by(parent_no=req.attr.parentNo).count()
    child_current_order = child_rel.child_order
    if childs_length == 1 or child_current_order == 1:
        return None

    upper_child_rel = TElementChildRel.query.filter_by(
        parent_no=req.attr.parentNo,
        child_order=child_current_order - 1
    ).first()
    upper_child_rel.child_order += 1
    child_rel.child_order -= 1

    upper_child_rel.save()
    child_rel.save()
    return None


@http_service
def move_down_element_child_order(req: RequestDTO):
    child_rel = TElementChildRel.query.filter_by(
        parent_no=req.attr.parentNo,
        child_no=req.attr.childNo
    ).first()
    Verify.not_empty(child_rel, '子元素不存在')

    childs_length = TElementChildRel.query.filter_by(parent_no=req.attr.parentNo).count()
    current_child_order = child_rel.child_order
    if childs_length == current_child_order:
        return None

    lower_child_rel = TElementChildRel.query.filter_by(
        parent_no=req.attr.parentNo,
        child_order=current_child_order + 1
    ).first()
    lower_child_rel.child_order -= 1
    child_rel.child_order += 1

    lower_child_rel.save()
    child_rel.save()
    return None


@http_service
def duplicate_element(req: RequestDTO):
    element = TTestElement.query.filter_by(element_no=req.attr.element_no).first()
    Verify.not_empty(element, '测试元素不存在')

    # todo 复制元素
    return None


def select_element(conditions: list, offset, limit) -> (int, list):
    """查询 TTestElement表
    """
    # 列表总数
    total_size = TTestElement.query.filter(*conditions).count()

    # 列表数据
    elements = TTestElement.query.filter(
        *conditions
    ).order_by(
        TTestElement.created_time.desc()
    ).offset(offset).limit(limit).all()

    return total_size, elements


def select_item_collection_rel_and_element(conditions: list, offset, limit) -> (int, list):
    """TItemCollectionRel，TTestElement连表查询
    """
    # 列表总数
    total_size = TTestElement.query.join(
        TItemCollectionRel, TItemCollectionRel.collection_no == TTestElement.element_no
    ).filter(*conditions).count()

    # 列表数据
    elements = TTestElement.query.join(
        TItemCollectionRel, TItemCollectionRel.collection_no == TTestElement.element_no
    ).filter(
        *conditions
    ).order_by(
        TTestElement.created_time.desc()
    ).offset(offset).limit(limit).all()

    return total_size, elements


def select_item_and_collection_rel_and_element(conditions: list, offset, limit) -> (int, list):
    """TTestItem，TItemCollectionRel，TTestElement连表查询
    """
    # 列表总数
    total_size = TTestElement.query.join(
        TItemCollectionRel, TItemCollectionRel.collection_no == TTestElement.element_no
    ).join(
        TTestItem, TTestItem.item_no == TItemCollectionRel.item_no
    ).filter(*conditions).count()

    # 列表数据
    elements = TTestElement.query.join(
        TItemCollectionRel, TItemCollectionRel.collection_no == TTestElement.element_no
    ).join(
        TTestItem, TTestItem.item_no == TItemCollectionRel.item_no
    ).filter(
        *conditions
    ).order_by(
        TTestElement.created_time.desc()
    ).offset(offset).limit(limit).all()

    return total_size, elements


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
            child_order=next_child_order(parent_no),
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
        modify_element_child_no_commit(child_list)


def modify_element_property_no_commit(element_no, propertys: dict):
    for prop_name, prop_value in propertys.items():
        el_prop = TElementProperty.query.filter_by(element_no=element_no, property_name=prop_name).first()
        el_prop.property_value = prop_value
        el_prop.save(commit=False)

    db.session.flush()


def modify_element_child_no_commit(child_list: [dict]):
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


def delete_element_no_commit(element_no):
    element = TTestElement.query.filter_by(element_no=element_no).first()
    Verify.not_empty(element, '测试元素不存在')

    result = [{
        'elementNo': element.element_no,
        'elementName': element.element_name
    }]

    # 递归删除元素子代和关联关系
    result.extend(delete_child_no_commit(element_no))
    # 如存在父辈关联关系，则删除关联并重新排序父辈子代
    child_rel = TElementChildRel.query.filter_by(child_no=element_no).first()
    if child_rel:
        # 重新排序父辈子代
        TElementChildRel.query.filter(
            TElementChildRel.parent_no == child_rel.parent_no,
            TElementChildRel.child_order > child_rel.child_order
        ).update({TElementChildRel.child_order: TElementChildRel.child_order - 1})
        # 删除父辈关联
        child_rel.delete(commit=False)

    # 删除元素属性
    delete_property_no_commit(element_no)
    # 删除元素
    element.delete(commit=False)

    db.session.flush()
    return result


def delete_child_no_commit(element_no):
    child_rels = TElementChildRel.query.filter_by(parent_no=element_no).all()
    result = []
    for child_rel in child_rels:
        # 查询子代元素信息
        child = TTestElement.query.filter_by(element_no=child_rel.child_no).first()
        if child:
            result.append({'elementNo': child.element_no, 'elementName': child.element_name})

        result.extend(delete_child_no_commit(child_rel.child_no))  # 递归删除子代元素的子代和关联关系
        # 删除父子关联关系
        child_rel.delete(commit=False)
        # 删除子代元素属性
        delete_property_no_commit(child_rel.child_no)
        # 删除子代元素
        child.delete(commit=False)

    db.session.flush()
    return result


def delete_property_no_commit(element_no):
    props = TElementProperty.query.filter_by(element_no=element_no).all()
    for prop in props:
        prop.delete(commit=False)

    db.session.flush()


def next_child_order(parent_no):
    return TElementChildRel.query.filter_by(parent_no=parent_no).count() + 1
