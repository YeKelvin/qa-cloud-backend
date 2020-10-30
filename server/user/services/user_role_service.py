#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_role_service
# @Time    : 2020/7/3 15:17
# @Author  : Kelvin.Ye
from server.extension import db
from server.common.decorators.service import http_service
from server.common.request import RequestDTO
from server.common.verify import Verify
from server.user.models import TUser, TUserRoleRel, TRole
from server.common.utils.log_util import get_logger

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

    if req.attr.userNo:
        conditions.append(TUserRoleRel.USER_NO.like(f'%{req.attr.userNo}%'))
    if req.attr.roleNo:
        conditions.append(TUserRoleRel.ROLE_NO.like(f'%{req.attr.roleNo}%'))
    if req.attr.roleName:
        conditions.append(TRole.ROLE_NAME.like(f'%{req.attr.roleName}%'))
    if req.attr.userName:
        conditions.append(TUser.USER_NAME.like(f'%{req.attr.userName}%'))

    pagination = db.session.query(
        TUserRoleRel.USER_NO,
        TUserRoleRel.ROLE_NO,
        TRole.ROLE_NAME,
        TUser.USER_NAME,
        TUserRoleRel.CREATED_TIME
    ).filter(*conditions).order_by(TUserRoleRel.CREATED_TIME.desc()).paginate(req.attr.page, req.attr.pageSize)

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
    user_role = TUserRoleRel.query_by(USER_NO=req.attr.userNo, ROLE_NO=req.attr.roleNo).first()
    Verify.empty(user_role, '用户角色关联关系已存在')

    TUserRoleRel.create(USER_NO=req.attr.userNo, ROLE_NO=req.attr.roleNo)
    return None


@http_service
def delete_user_role_rel(req: RequestDTO):
    user_role = TUserRoleRel.query_by(USER_NO=req.attr.userNo, ROLE_NO=req.attr.roleNo).first()
    Verify.not_empty(user_role, '用户角色关联关系不存在')

    user_role.update(DEL_STATE=1)
    return None
