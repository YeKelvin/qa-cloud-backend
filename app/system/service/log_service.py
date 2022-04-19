#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_service.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from app.extension import db
from app.common.decorators.service import http_service
from app.system.model import TSystemOperationLog
from app.usercenter.model import TPermission
from app.utils.log_util import get_logger
from app.utils.time_util import STRFTIME_FORMAT
from app.utils.sqlalchemy_util import QueryCondition

log = get_logger(__name__)


@http_service
def query_operation_log_list(req):
    # 查询条件
    conds = QueryCondition(TSystemOperationLog, TPermission)
    conds.like(TPermission.PERMISSION_NAME, req.operationName)
    conds.like(TSystemOperationLog.OPERATION_METHOD, req.operationMethod)
    conds.like(TSystemOperationLog.OPERATION_ENDPOINT, req.operationEndpoint)
    conds.like(TSystemOperationLog.CREATED_BY, req.createdBy)
    conds.ge(TSystemOperationLog.CREATED_TIMECREATED_TIME, req.startTime)
    conds.le(TSystemOperationLog.CREATED_TIME, req.endTime)
    conds.equal(TSystemOperationLog.OPERATION_METHOD, TPermission.METHOD)
    conds.equal(TSystemOperationLog.OPERATION_ENDPOINT, TPermission.ENDPOINT)

    # 查询日志列表
    pagination = db.session.query(
        TPermission.PERMISSION_NAME,
        TSystemOperationLog.OPERATION_METHOD,
        TSystemOperationLog.OPERATION_ENDPOINT,
        TSystemOperationLog.CREATED_BY,
        TSystemOperationLog.CREATED_TIME,
    ).filter(*conds).order_by(TSystemOperationLog.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for item in pagination.items:
        data.append({
            'operationName': item.ACTION_DESC,
            'operationMethod': item.ACTION_METHOD,
            'operationEndpoint': item.ACTION_ENDPOINT,
            'createdTime': item.CREATED_TIME.strftime(STRFTIME_FORMAT),
            'createdBy': item.CREATED_BY,
        })

    return {'data': data, 'total': pagination.total}
