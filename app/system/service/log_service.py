#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_service.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.logger import get_logger
from app.extension import db
from app.system.model import TSystemOperationLog
from app.usercenter.model import TPermission
from app.usercenter.model import TUser
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import STRFTIME_FORMAT


log = get_logger(__name__)


@http_service
def query_operation_log_list(req):
    # 查询条件
    conds = QueryCondition(TSystemOperationLog, TPermission, TUser)
    conds.like(TUser.USER_NAME, req.operationBy)
    conds.like(TPermission.PERMISSION_NAME, req.operationName)
    conds.like(TSystemOperationLog.OPERATION_METHOD, req.operationMethod)
    conds.like(TSystemOperationLog.OPERATION_ENDPOINT, req.operationEndpoint)
    conds.ge(TSystemOperationLog.CREATED_TIME, req.startTime)
    conds.le(TSystemOperationLog.CREATED_TIME, req.endTime)
    conds.equal(TSystemOperationLog.OPERATION_METHOD, TPermission.METHOD)
    conds.equal(TSystemOperationLog.OPERATION_ENDPOINT, TPermission.ENDPOINT)
    conds.equal(TSystemOperationLog.CREATED_BY, TUser.USER_NO)

    # 查询日志列表
    pagination = db.session.query(
        TUser.USER_NAME,
        TPermission.PERMISSION_NAME,
        TSystemOperationLog.OPERATION_METHOD,
        TSystemOperationLog.OPERATION_ENDPOINT,
        TSystemOperationLog.CREATED_TIME,
    ).filter(*conds).order_by(TSystemOperationLog.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for item in pagination.items:
        data.append({
            'operationMethod': item.OPERATION_METHOD,
            'operationEndpoint': item.OPERATION_ENDPOINT,
            'operationName': item.PERMISSION_NAME,
            'operationBy': item.USER_NAME,
            'operationTime': item.CREATED_TIME.strftime(STRFTIME_FORMAT)
        })

    return {'data': data, 'total': pagination.total}
