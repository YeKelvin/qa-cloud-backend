#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2019/11/14 9:51
# @Author  : Kelvin.Ye
from server.common.number_generator import generate_item_no
from server.librarys.decorators.service import http_service
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.verify import Verify
from server.script.model import TTestItem
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_item_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = [TTestItem.DEL_STATE == 0]
    if req.attr.itemNo:
        conditions.append(TTestItem.ITEM_NO.like(f'%{req.attr.itemNo}%'))
    if req.attr.itemName:
        conditions.append(TTestItem.ITEM_NAME.like(f'%{req.attr.itemName}%'))
    if req.attr.itemDesc:
        conditions.append(TTestItem.ITEM_DESC.like(f'%{req.attr.itemDesc}%'))

    # 列表总数
    total_size = TTestItem.query.filter(*conditions).count()

    # 列表数据
    items = TTestItem.query.filter(
        *conditions
    ).order_by(
        TTestItem.CREATED_TIME.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for item in items:
        data_set.append({
            'itemNo': item.ITEM_NO,
            'itemName': item.ITEM_NAME,
            'itemDesc': item.ITEM_DESC
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def query_item_all():
    items = TTestItem.query.filter_by(DEL_STATE=0).order_by(TTestItem.CREATED_TIME.desc()).all()
    result = []
    for item in items:
        result.append({
            'itemNo': item.ITEM_NO,
            'itemName': item.ITEM_NAME,
            'itemDesc': item.ITEM_DESC
        })
    return result


@http_service
def create_item(req: RequestDTO):
    item = TTestItem.query.filter_by(ITEM_NAME=req.attr.itemName, DEL_STATE=0).first()
    Verify.empty(item, '测试项目已存在')

    TTestItem.create(
        ITEM_NO=generate_item_no(),
        ITEM_NAME=req.attr.itemName,
        ITEM_DESC=req.attr.itemDesc
    )
    return None


@http_service
def modify_item(req: RequestDTO):
    item = TTestItem.query.filter_by(ITEM_NO=req.attr.itemNo, DEL_STATE=0).first()
    Verify.not_empty(item, '测试项目不存在')

    if req.attr.itemName is not None:
        item.ITEM_NAME = req.attr.itemName
    if req.attr.itemDesc is not None:
        item.ITEM_DESC = req.attr.itemDesc

    item.save()
    return None


@http_service
def delete_item(req: RequestDTO):
    item = TTestItem.query.filter_by(ITEM_NO=req.attr.itemNo, DEL_STATE=0).first()
    Verify.not_empty(item, '测试项目不存在')

    item.update(DEL_STATE=1)
    return None


@http_service
def add_item_user(req: RequestDTO):
    pass


@http_service
def modify_item_user(req: RequestDTO):
    pass


@http_service
def remove_item_user(req: RequestDTO):
    pass
