#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from server.librarys.decorators.service import http_service
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.system.model import TActionLog
from server.utils.log_util import get_logger
from server.utils.time_util import STRFTIME_FORMAT

log = get_logger(__name__)


@http_service
def query_action_log_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    if req.attr.actionDesc:
        conditions.append(TActionLog.ACTION_DESC.like(f'%{req.attr.actionDesc}%'))
    if req.attr.actionMethod:
        conditions.append(TActionLog.ACTION_METHOD.like(f'%{req.attr.actionMethod}%'))
    if req.attr.actionEndpoint:
        conditions.append(TActionLog.ACTION_ENDPOINT.like(f'%{req.attr.actionEndpoint}%'))
    if req.attr.startTime:
        conditions.append(TActionLog.CREATED_TIME >= req.attr.startTime)
    if req.attr.endTime:
        conditions.append(TActionLog.CREATED_TIME <= req.attr.endTime)
    if req.attr.createdBy:
        conditions.append(TActionLog.CREATED_BY.like(f'%{req.attr.createdBy}%'))

    # 列表总数
    total_size = TActionLog.query.filter(*conditions).count()
    # 列表数据
    logs = TActionLog.query.filter(
        *conditions
    ).order_by(
        TActionLog.CREATED_TIME.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for log in logs:
        data_set.append({
            'actionDesc': log.ACTION_DESC,
            'actionMethod': log.ACTION_METHOD,
            'actionEndpoint': log.ACTION_ENDPOINT,
            'oldValue': log.OLD_VALUE,
            'newValue': log.NEW_VALUE,
            'createdTime': log.CREATED_TIME.strftime(STRFTIME_FORMAT),
            'createdBy': log.CREATED_BY,
        })

    return {'dataSet': data_set, 'totalSize': total_size}
