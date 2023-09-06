#!/usr/bin python3
# @File    : login_log_service.py
# @Time    : 2023-09-06 16:13:57
# @Author  : Kelvin.Ye
from app.database import dbquery
from app.modules.usercenter.model import TUser
from app.modules.usercenter.model import TUserLoginLog
from app.tools.service import http_service
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import TIMEFMT


@http_service
def query_login_log_list(req):
    # 查询条件
    conds = QueryCondition(TUserLoginLog, TUser)
    conds.like(TUser.USER_NAME, req.userName)
    conds.like(TUserLoginLog.LOGIN_NAME, req.loginName)
    conds.like(TUserLoginLog.LOGIN_IP, req.loginIp)
    conds.equal(TUserLoginLog.LOGIN_TYPE, req.loginType)
    conds.equal(TUserLoginLog.LOGIN_METHOD, req.loginMethod)
    conds.equal(TUserLoginLog.USER_NO, TUser.USER_NO)
    conds.ge(TUserLoginLog.CREATED_TIME, req.startTime)
    conds.le(TUserLoginLog.CREATED_TIME, req.endTime)

    # 查询日志列表
    pagination = (
        dbquery(
            TUser.USER_NAME,
            TUserLoginLog.LOGIN_NAME,
            TUserLoginLog.LOGIN_TYPE,
            TUserLoginLog.LOGIN_METHOD,
            TUserLoginLog.LOGIN_IP,
            TUserLoginLog.CREATED_TIME
        )
        .filter(*conds)
        .order_by(TUserLoginLog.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'userName': item.USER_NAME,
            'loginName': item.LOGIN_NAME,
            'loginType': item.LOGIN_TYPE,
            'loginMethod': item.LOGIN_METHOD,
            'loginIp': item.LOGIN_IP,
            'loginTime': item.CREATED_TIME.strftime(TIMEFMT)
        }
        for item in pagination.items
    ]

    return {'data': data, 'total': pagination.total}
