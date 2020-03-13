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
def action_log_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    if req.attr.actionDetail:
        conditions.append(TActionLog.action_detail.like(f'%{req.attr.actionDetail}%'))
    if req.attr.actionPath:
        conditions.append(TActionLog.action_path.like(f'%{req.attr.actionPath}%'))
    if req.attr.startTime:
        conditions.append(TActionLog.created_time >= req.attr.startTime)
    if req.attr.endTime:
        conditions.append(TActionLog.created_time <= req.attr.endTime)
    if req.attr.createdBy:
        conditions.append(TActionLog.created_by.like(f'%{req.attr.createdBy}%'))

    # 列表总数
    total_size = TActionLog.query.filter(*conditions).count()
    # 列表数据
    action_logs = TActionLog.query.filter(
        *conditions
    ).order_by(
        TActionLog.created_time.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for action_log in action_logs:
        data_set.append({
            'actionDetail': action_log.action_detail,
            'actionPath': action_log.action_path,
            'description': action_log.description,
            'createdTime': action_log.created_time.strftime(STRFTIME_FORMAT),
            'createdBy': action_log.created_by,
        })

    return {'dataSet': data_set, 'totalSize': total_size}
