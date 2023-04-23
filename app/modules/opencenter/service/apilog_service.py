#!/usr/bin python3
# @File    : apilog_service.py
# @Time    : 2023-04-21 09:07:58
# @Author  : Kelvin.Ye
from app.database import dbquery
from app.modules.opencenter.model import TOpenApiLog
from app.modules.opencenter.model import TThirdPartyApplication
from app.tools.service import http_service
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import TIMEFMT


@http_service
def query_openapi_log_list(req):
        # 查询条件
    conds = QueryCondition(TOpenApiLog, TThirdPartyApplication)
    conds.like(TThirdPartyApplication.APP_NAME, req.appName)
    conds.like(TOpenApiLog.METHOD, req.method)
    conds.like(TOpenApiLog.URI, req.path)
    conds.like(TOpenApiLog.REQUEST, req.request)
    conds.like(TOpenApiLog.RESPONSE, req.response)
    conds.equal(TOpenApiLog.SUCCESS, req.success)
    conds.ge(TOpenApiLog.CREATED_TIME, req.startTime)
    conds.le(TOpenApiLog.CREATED_TIME, req.endTime)
    conds.equal(TOpenApiLog.APP_NO, TThirdPartyApplication.APP_NO)

    # 查询日志列表
    pagination = (
        dbquery(
            TThirdPartyApplication.APP_NAME,
            TOpenApiLog.LOG_NO,
            TOpenApiLog.IP,
            TOpenApiLog.METHOD,
            TOpenApiLog.URI,
            TOpenApiLog.REQUEST,
            TOpenApiLog.RESPONSE,
            TOpenApiLog.SUCCESS,
            TOpenApiLog.ELAPSED_TIME,
            TOpenApiLog.CREATED_TIME
        )
        .filter(*conds)
        .order_by(TOpenApiLog.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize)
    )

    data = [
        {
            'logNo': entity.LOG_NO,
            'method': entity.METHOD,
            'path': entity.URI,
            'request': entity.REQUEST,
            'response': entity.RESPONSE,
            'success': entity.SUCCESS,
            'elapsedTime': entity.ELAPSED_TIME,
            'appName': entity.APP_NAME,
            'invokeIp': entity.IP,
            'invokeTime': entity.CREATED_TIME.strftime(TIMEFMT)
        }
        for entity in pagination.items
    ]

    return {'data': data, 'total': pagination.total}
