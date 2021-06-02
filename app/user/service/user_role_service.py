#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_role_service.py
# @Time    : 2020/7/3 15:17
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.request import RequestDTO
from app.common.validator import assert_blank
from app.common.validator import assert_not_blank
from app.extension import db
from app.user.model import TRole
from app.user.model import TUser
from app.user.model import TUserRoleRel
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_user_role_rel_list(req: RequestDTO):
    # 查询条件
    conditions = [
        TUser.DEL_STATE == 0,
        TRole.DEL_STATE == 0,
        TUserRoleRel.DEL_STATE == 0,
        TUser.USER_NO == TUserRoleRel.USER_NO,
        TRole.ROLE_NO == TUserRoleRel.ROLE_NO
    ]

    if req.userNo:
        conditions.append(TUserRoleRel.USER_NO.like(f'%{req.userNo}%'))
    if req.roleNo:
        conditions.append(TUserRoleRel.ROLE_NO.like(f'%{req.roleNo}%'))
    if req.roleName:
        conditions.append(TRole.ROLE_NAME.like(f'%{req.roleName}%'))
    if req.userName:
        conditions.append(TUser.USER_NAME.like(f'%{req.userName}%'))

    pagination = db.session.query(
        TUserRoleRel.USER_NO,
        TUserRoleRel.ROLE_NO,
        TRole.ROLE_NAME,
        TUser.USER_NAME,
        TUserRoleRel.CREATED_TIME
    ).filter(*conditions).order_by(TUserRoleRel.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    # 组装数据
    data_set = []
    for item in pagination.items:
        data_set.append({
            'userNo': item.USER_NO,
            'roleNo': item.ROLE_NO,
            'userName': item.USER_NAME,
            'roleName': item.ROLE_NAME,
        })

    return {'dataSet': data_set, 'totalSize': pagination.total}


@http_service
def create_user_role_rel(req: RequestDTO):
    user_role = TUserRoleRel.query_by(USER_NO=req.userNo, ROLE_NO=req.roleNo).first()
    assert_blank(user_role, '用户角色关联关系已存在')

    TUserRoleRel.create(USER_NO=req.userNo, ROLE_NO=req.roleNo)
    return None


@http_service
def delete_user_role_rel(req: RequestDTO):
    user_role = TUserRoleRel.query_by(USER_NO=req.userNo, ROLE_NO=req.roleNo).first()
    assert_not_blank(user_role, '用户角色关联关系不存在')

    user_role.update(DEL_STATE=1)
    return None
