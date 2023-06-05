#!/usr/bin/ python3
# @File    : log_service.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from app.database import dbquery
from app.modules.system.model import TRestApiLog
from app.modules.usercenter.model import TUser
from app.tools.service import http_service
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import TIMEFMT


@http_service
def query_restapi_log_list(req):
    # 查询条件
    conds = QueryCondition(TRestApiLog, TUser)
    conds.like(TUser.USER_NAME, req.invokeBy)
    conds.like(TRestApiLog.METHOD, req.method)
    conds.like(TRestApiLog.URI, req.path)
    conds.equal(TRestApiLog.REQUEST, req.request)
    conds.equal(TRestApiLog.RESPONSE, req.response)
    conds.equal(TRestApiLog.SUCCESS, req.success)
    conds.ge(TRestApiLog.CREATED_TIME, req.startTime)
    conds.le(TRestApiLog.CREATED_TIME, req.endTime)
    conds.equal(TRestApiLog.CREATED_BY, TUser.USER_NO)

    # 查询日志列表
    pagination = (
        dbquery(
            TUser.USER_NAME,
            TRestApiLog.LOG_NO,
            TRestApiLog.IP,
            TRestApiLog.METHOD,
            TRestApiLog.URI,
            TRestApiLog.DESC,
            TRestApiLog.REQUEST,
            TRestApiLog.RESPONSE,
            TRestApiLog.SUCCESS,
            TRestApiLog.ELAPSED_TIME,
            TRestApiLog.CREATED_TIME,
        )
        .filter(*conds)
        .order_by(TRestApiLog.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'logNo': item.LOG_NO,
            'method': item.METHOD,
            'path': item.URI,
            'desc': item.DESC,
            'request': item.REQUEST,
            'response': item.RESPONSE,
            'success': item.SUCCESS,
            'elapsedTime': item.ELAPSED_TIME,
            'invokeBy': item.USER_NAME,
            'invokeIp': item.IP,
            'invokeTime': item.CREATED_TIME.strftime(TIMEFMT)
        }
        for item in pagination.items
    ]

    return {'data': data, 'total': pagination.total}
