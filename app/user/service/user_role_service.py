#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_role_service.py
# @Time    : 2020/7/3 15:17
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.extension import db
from app.user.dao import user_role_rel_dao as UserRoleRelDao
from app.user.model import TRole
from app.user.model import TUser
from app.user.model import TUserRoleRel
from app.utils.log_util import get_logger
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_user_role_rel_list(req):
    # 查询条件
    conds = QueryCondition(TUser, TRole, TUserRoleRel)
    conds.equal(TUser.USER_NO, TUserRoleRel.USER_NO)
    conds.equal(TRole.ROLE_NO, TUserRoleRel.ROLE_NO)
    conds.like(TUser.USER_NAME, req.userName)
    conds.like(TRole.ROLE_NAME, req.roleName)
    conds.like(TUserRoleRel.USER_NO, req.userNo)
    conds.like(TUserRoleRel.ROLE_NO, req.roleNo)

    # TUser，TRole，TUserRoleRel连表查询
    pagination = db.session.query(
        TUser.USER_NAME,
        TRole.ROLE_NAME,
        TUserRoleRel.USER_NO,
        TUserRoleRel.ROLE_NO,
        TUserRoleRel.CREATED_TIME
    ).filter(*conds).order_by(TUserRoleRel.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for item in pagination.items:
        data.append({
            'userNo': item.USER_NO,
            'roleNo': item.ROLE_NO,
            'userName': item.USER_NAME,
            'roleName': item.ROLE_NAME,
        })

    return {'data': data, 'total': pagination.total}


@http_service
def create_user_role_rel(req):
    # 查询用户角色
    user_role = UserRoleRelDao.select_by_userno_and_roleno(req.userNo, req.roleNo)
    check_is_blank(user_role, '用户角色关联已存在')

    # 绑定用户和角色
    TUserRoleRel.insert(USER_NO=req.userNo, ROLE_NO=req.roleNo)


@http_service
def remove_user_role_rel(req):
    # 查询用户角色
    user_role = UserRoleRelDao.select_by_userno_and_roleno(req.userNo, req.roleNo)
    check_is_not_blank(user_role, '用户角色关联不存在')

    # 解绑用户和角色
    user_role.delete()
