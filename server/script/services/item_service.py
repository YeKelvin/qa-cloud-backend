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

    # 列表总数
    total_size = 0

    # 列表数据

    # 组装响应数据


@http_service
def item_all(req: RequestDTO):
    """查询所有测试项目
    """
    pass


@http_service
def create_item(req: RequestDTO):
    """新增测试项目
    """
    permission = TTestItem.query.filter_by(endpoint=req.attr.endpoint, method=req.attr.method).first()
    Verify.empty(permission, '权限已存在')

    TTestItem.create(
        permission_no=generate_item_no(),
        permission_name=req.attr.permissionName,
        endpoint=req.attr.endpoint,
        method=req.attr.method,
        state='NORMAL',
        description=req.attr.description,
        created_time=datetime.now(),
        created_by=Global.operator,
        updated_time=datetime.now(),
        updated_by=Global.operator
    )
    return None


@http_service
def modify_item(req: RequestDTO):
    """修改测试项目
    """
    pass


@http_service
def delete_item(req: RequestDTO):
    """删除测试项目
    """
    pass


def generate_item_no():
    pass
