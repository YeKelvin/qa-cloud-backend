#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_service.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.request import RequestDTO
from app.system.model import TActionLog
from app.utils.log_util import get_logger
from app.utils.time_util import STRFTIME_FORMAT


log = get_logger(__name__)


@http_service
def query_action_log_list(req: RequestDTO):
    # 查询条件
    conditions = []
    if req.actionDesc:
        conditions.append(TActionLog.ACTION_DESC.like(f'%{req.actionDesc}%'))
    if req.actionMethod:
        conditions.append(TActionLog.ACTION_METHOD.like(f'%{req.actionMethod}%'))
    if req.actionEndpoint:
        conditions.append(TActionLog.ACTION_ENDPOINT.like(f'%{req.actionEndpoint}%'))
    if req.startTime:
        conditions.append(TActionLog.CREATED_TIME >= req.startTime)
    if req.endTime:
        conditions.append(TActionLog.CREATED_TIME <= req.endTime)
    if req.createdBy:
        conditions.append(TActionLog.CREATED_BY.like(f'%{req.createdBy}%'))

    pagination = TActionLog.query.filter(
        *conditions).order_by(TActionLog.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

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
