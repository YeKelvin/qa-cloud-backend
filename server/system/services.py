#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from server.common.decorators.service import http_service
from server.common.request import RequestDTO
from server.system.models import TActionLog
from server.common.utils.log_util import get_logger
from server.common.utils.time_util import STRFTIME_FORMAT

log = get_logger(__name__)


@http_service
def query_action_log_list(req: RequestDTO):
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

    pagination = TActionLog.query.filter(
        *conditions).order_by(TActionLog.CREATED_TIME.desc()).paginate(req.attr.page, req.attr.pageSize)

    # 组装数据
    data_set = []
    for item in pagination.items:
        data_set.append({
            'actionDesc': item.ACTION_DESC,
            'actionMethod': item.ACTION_METHOD,
            'actionEndpoint': item.ACTION_ENDPOINT,
            'oldValue': item.OLD_VALUE,
            'newValue': item.NEW_VALUE,
            'createdTime': item.CREATED_TIME.strftime(STRFTIME_FORMAT),
            'createdBy': item.CREATED_BY,
        })

    return {'dataSet': data_set, 'totalSize': pagination.total}
