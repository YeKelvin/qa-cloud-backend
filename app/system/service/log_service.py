#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_service.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from app.database import dbquery
from app.system.model import TSystemOperationLog
from app.tools.decorators.service import http_service
from app.usercenter.model import TUser
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import STRFTIME_FORMAT


@http_service
def query_operation_log_list(req):
    # 查询条件
    conds = QueryCondition(TSystemOperationLog, TUser)
    conds.like(TUser.USER_NAME, req.operationBy)
    conds.like(TSystemOperationLog.OPERATION_METHOD, req.operationMethod)
    conds.like(TSystemOperationLog.OPERATION_ENDPOINT, req.operationEndpoint)
    conds.ge(TSystemOperationLog.CREATED_TIME, req.startTime)
    conds.le(TSystemOperationLog.CREATED_TIME, req.endTime)
    conds.equal(TSystemOperationLog.CREATED_BY, TUser.USER_NO)

    # 查询日志列表
    pagination = (
        dbquery(
            TUser.USER_NAME,
            TSystemOperationLog.LOG_NO,
            TSystemOperationLog.OPERATION_METHOD,
            TSystemOperationLog.OPERATION_ENDPOINT,
            TSystemOperationLog.CREATED_TIME,
        )
        .filter(*conds)
        .order_by(TSystemOperationLog.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize)
    )

    data = [
        {
            'logNo': item.LOG_NO,
            'operationMethod': item.OPERATION_METHOD,
            'operationEndpoint': item.OPERATION_ENDPOINT,
            'operationBy': item.USER_NAME,
            'operationTime': item.CREATED_TIME.strftime(STRFTIME_FORMAT)
        }
        for item in pagination.items
    ]

    return {'data': data, 'total': pagination.total}
