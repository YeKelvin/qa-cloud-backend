#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_user_service.py
# @Time    : 2021/6/5 23:39
# @Author  : Kelvin.Ye
from app.extension import db
from app.public.dao import workspace_dao as WorkspaceDao
from app.public.dao import workspace_user_dao as WorkspaceUserDao
from app.public.model import TWorkspace
from app.public.model import TWorkspaceUser
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.exceptions import ServiceError
from app.tools.logger import get_logger
from app.tools.validator import check_exists
from app.usercenter.model import TRole
from app.usercenter.model import TUser
from app.usercenter.model import TUserRole
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_workspace_user_list(req):
    # 查询条件
    conds = QueryCondition(TUser, TWorkspace, TWorkspaceUser)
    conds.equal(TUser.USER_NO, TWorkspaceUser.USER_NO)
    conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceUser.WORKSPACE_NO)
    conds.like(TWorkspaceUser.WORKSPACE_NO, req.workspaceNo)

    # TUser, TWorkspace, TWorkspaceUser 连表查询
    pagination = db.session.query(
        TWorkspace.WORKSPACE_NO,
        TWorkspace.WORKSPACE_NAME,
        TUser.USER_NO,
        TUser.USER_NAME
    ).filter(*conds).order_by(TWorkspaceUser.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for item in pagination.items:
        data.append({
            'workspaceNo': item.WORKSPACE_NO,
            'workspaceName': item.WORKSPACE_NAME,
            'userNo': item.USER_NO,
            'userName': item.USER_NAME,
        })

    return {'data': data, 'total': pagination.total}


@http_service
def query_workspace_user_all(req):
    # 查询条件
    conds = QueryCondition(TUser, TWorkspaceUser)
    conds.equal(TUser.USER_NO, TWorkspaceUser.USER_NO)
    conds.equal(TWorkspaceUser.WORKSPACE_NO, req.workspaceNo)

    # 查询所有空间成员
    workspace_user_list = db.session.query(
        TUser.USER_NO,
        TUser.USER_NAME
    ).filter(*conds).order_by(TUser.CREATED_TIME.desc()).all()

    result = []
    for user in workspace_user_list:
        result.append({
            'userNo': user.USER_NO,
            'userName': user.USER_NAME
        })
    return result


@http_service
@transactional
def modify_workspace_user(req):
    # 查询元素
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')

    # 成员列表添加超级管理用户编号
    user_numbered_list = req.userNumberList
    user_numbered_list.append(get_super_admin_userno())

    # 更新空间成员
    for user_no in user_numbered_list:
        # 查询空间成员
        workspace_user = WorkspaceUserDao.select_by_workspace_and_user(req.workspaceNo, user_no)
        if workspace_user:
            continue
        else:
            # 新增空间成员
            TWorkspaceUser.insert(WORKSPACE_NO=req.workspaceNo, USER_NO=user_no)

    # 删除不在请求中的空间成员
    WorkspaceUserDao.delete_all_by_workspace_and_notin_user(req.workspaceNo, user_numbered_list)


def get_super_admin_userno():
    # 查询条件
    conds = QueryCondition(TUser, TRole, TUserRole)
    conds.equal(TUser.USER_NO, TUserRole.USER_NO)
    conds.equal(TRole.ROLE_NO, TUserRole.ROLE_NO)
    conds.equal(TRole.ROLE_CODE, 'SUPER_ADMIN')

    # 查询超级管理员的用户编号
    if result := db.session.query(TUser.USER_NO).filter(*conds).first():
        return result[0]
    else:
        raise ServiceError('查询超级管理员用户失败')
