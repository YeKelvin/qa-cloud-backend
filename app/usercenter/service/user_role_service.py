#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_role_service.py
# @Time    : 2020/7/3 15:17
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.extension import db
from app.usercenter.model import TRole
from app.usercenter.model import TUser
from app.usercenter.model import TUserRole
from app.utils.log_util import get_logger
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_user_role_list(req):
    # 查询条件
    conds = QueryCondition(TUser, TRole, TUserRole)
    conds.equal(TUser.USER_NO, TUserRole.USER_NO)
    conds.equal(TRole.ROLE_NO, TUserRole.ROLE_NO)
    conds.like(TUser.USER_NAME, req.userName)
    conds.like(TRole.ROLE_NAME, req.roleName)
    conds.like(TRole.ROLE_CODE, req.roleCode)
    conds.like(TUserRole.USER_NO, req.userNo)
    conds.like(TUserRole.ROLE_NO, req.roleNo)

    # TUser，TRole，TUserRole连表查询
    pagination = db.session.query(
        TUser.USER_NAME,
        TRole.ROLE_NAME,
        TRole.ROLE_CODE,
        TUserRole.USER_NO,
        TUserRole.ROLE_NO,
        TUserRole.CREATED_TIME
    ).filter(*conds).order_by(TUserRole.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for item in pagination.items:
        data.append({
            'userNo': item.USER_NO,
            'roleNo': item.ROLE_NO,
            'userName': item.USER_NAME,
            'roleName': item.ROLE_NAME,
            'roleCode': item.ROLE_CODE,
        })

    return {'data': data, 'total': pagination.total}


@http_service
def query_user_role_all(req):
    # 查询条件
    conds = QueryCondition(TUser, TRole, TUserRole)
    conds.equal(TUser.USER_NO, TUserRole.USER_NO)
    conds.equal(TRole.ROLE_NO, TUserRole.ROLE_NO)
    conds.like(TUser.USER_NAME, req.userName)
    conds.like(TRole.ROLE_NAME, req.roleName)
    conds.like(TRole.ROLE_CODE, req.roleCode)
    conds.like(TUserRole.USER_NO, req.userNo)
    conds.like(TUserRole.ROLE_NO, req.roleNo)

    # TUser，TRole，TUserRole连表查询
    entities = db.session.query(
        TUser.USER_NAME,
        TRole.ROLE_NAME,
        TRole.ROLE_CODE,
        TUserRole.USER_NO,
        TUserRole.ROLE_NO,
        TUserRole.CREATED_TIME
    ).filter(*conds).order_by(TUserRole.CREATED_TIME.desc()).all()

    result = []
    for entity in entities:
        result.append({
            'userNo': entity.USER_NO,
            'roleNo': entity.ROLE_NO,
            'userName': entity.USER_NAME,
            'roleName': entity.ROLE_NAME,
            'roleCode': entity.ROLE_CODE,
        })

    return result
