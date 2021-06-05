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
    conditions = QueryCondition()
    conditions.add_fully_match(TUser.DEL_STATE, 0)
    conditions.add_fully_match(TRole.DEL_STATE, 0)
    conditions.add_fully_match(TUserRoleRel.DEL_STATE, 0)
    conditions.add_fully_match(TUser.USER_NO, TUserRoleRel.USER_NO)
    conditions.add_fully_match(TRole.ROLE_NO, TUserRoleRel.ROLE_NO)
    conditions.add_fuzzy_match(TUserRoleRel.USER_NO, req.userNo)
    conditions.add_fuzzy_match(TUserRoleRel.ROLE_NO, req.roleNo)
    conditions.add_fuzzy_match(TRole.ROLE_NAME, req.roleName)
    conditions.add_fuzzy_match(TUser.USER_NAME, req.userName)

    results = db.session.query(
        TUserRoleRel.USER_NO,
        TUserRoleRel.ROLE_NO,
        TRole.ROLE_NAME,
        TUser.USER_NAME,
        TUserRoleRel.CREATED_TIME
    ).filter(*conditions).order_by(TUserRoleRel.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for result in results.items:
        data.append({
            'userNo': result.USER_NO,
            'roleNo': result.ROLE_NO,
            'userName': result.USER_NAME,
            'roleName': result.ROLE_NAME,
        })

    return {'data': data, 'total': results.total}


@http_service
def create_user_role_rel(req):
    user_role = UserRoleRelDao.select_by_userno_and_roleno(req.userNo, req.roleNo)
    check_is_blank(user_role, '用户角色关联关系已存在')

    TUserRoleRel.insert(USER_NO=req.userNo, ROLE_NO=req.roleNo)


@http_service
def delete_user_role_rel(req):
    user_role = UserRoleRelDao.select_by_userno_and_roleno(req.userNo, req.roleNo)
    check_is_not_blank(user_role, '用户角色关联关系不存在')

    user_role.update(DEL_STATE=1)
