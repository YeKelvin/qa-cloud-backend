#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2019/11/14 9:51
# @Author  : Kelvin.Ye
from datetime import datetime

from server.librarys.decorators.service import http_service
from server.librarys.helpers.global_helper import Global
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.sequence import Sequence
from server.librarys.verify import Verify
from server.script.model import TTestItem
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def item_list(req: RequestDTO):
    """分页查询测试项目列表
    """
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    if req.attr.itemNo:
        conditions.append(TTestItem.item_no == req.attr.itemNo)
    if req.attr.itemName:
        conditions.append(TTestItem.item_name.like(f'%{req.attr.itemName}%'))
    if req.attr.itemDescription:
        conditions.append(TTestItem.item_description.like(f'%{req.attr.itemDescription}%'))

    # 列表总数
    total_size = TTestItem.query.filter(*conditions).count()

    # 列表数据
    items = TTestItem.query.filter(
        *conditions
    ).order_by(
        TTestItem.created_time.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for item in items:
        data_set.append({
            'itemNo': item.item_no,
            'itemName': item.item_name,
            'itemDescription': item.item_description
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def item_all():
    """查询所有测试项目
    """
    items = TTestItem.query.order_by(TTestItem.created_time.desc()).all()
    result = []
    for item in items:
        result.append({
            'itemNo': item.item_no,
            'itemName': item.item_name,
            'itemDescription': item.item_description
        })
    return result


@http_service
def create_item(req: RequestDTO):
    """新增测试项目
    """
    item = TTestItem.query.filter_by(item_name=req.attr.itemName).first()
    Verify.empty(item, '测试项目已存在')

    TTestItem.create(
        item_no=generate_item_no(),
        item_name=req.attr.itemName,
        item_description=req.attr.itemDescription,
        created_by=Global.operator,
        created_time=datetime.now(),
        updated_by=Global.operator,
        updated_time=datetime.now()
    )
    return None


@http_service
def modify_item(req: RequestDTO):
    """修改测试项目
    """
    item = TTestItem.query.filter_by(item_no=req.attr.itemNo).first()
    Verify.not_empty(item, '测试项目不存在')

    if req.attr.itemName:
        item.item_name = req.attr.itemName
    if req.attr.itemDescription:
        item.item_description = req.attr.itemDescription

    item.save()
    return None


@http_service
def delete_item(req: RequestDTO):
    """删除测试项目
    """
    item = TTestItem.query.filter_by(item_no=req.attr.itemNo).first()
    Verify.not_empty(item, '测试项目不存在')

    item.delete()
    return None


def generate_item_no():
    seq_item_no = Sequence('seq_item_no')
    return 'ITEM' + str(seq_item_no.next_value()).zfill(8)
