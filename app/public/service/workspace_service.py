#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_service.py
# @Time    : 2019/11/14 9:51
# @Author  : Kelvin.Ye
from app.extension import db
from app.public.dao import workspace_dao as WorkspaceDao
from app.public.dao import workspace_restricted_exemption_dao as WorkspaceRestrictedExemptionDao
from app.public.dao import workspace_restriction_dao as WorkspaceRestrictionDao
from app.public.dao import workspace_user_dao as WorkspaceUserDao
from app.public.enum import WorkspaceScope
from app.public.model import TWorkspace
from app.public.model import TWorkspaceUser
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.logger import get_logger
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.usercenter.model import TRole
from app.usercenter.model import TUser
from app.usercenter.model import TUserRole
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_workspace_list(req):
    workspaces = WorkspaceDao.select_list(
        workspaceNo=req.workspaceNo,
        workspaceName=req.workspaceName,
        workspaceScope=req.workspaceScope,
        workspaceDesc=req.workspaceDesc,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for workspace in workspaces.items:
        data.append({
            'workspaceNo': workspace.WORKSPACE_NO,
            'workspaceName': workspace.WORKSPACE_NAME,
            'workspaceScope': workspace.WORKSPACE_SCOPE,
            'workspaceDesc': workspace.WORKSPACE_DESC
        })
    return {'data': data, 'total': workspaces.total}


@http_service
def query_workspace_all(req):
    if not req.userNo:
        workspaces = TWorkspace.filter_by().order_by(TWorkspace.CREATED_TIME.desc()).all()
    else:
        # 查询条件
        conds = QueryCondition(TWorkspace, TWorkspaceUser)
        conds.equal(TWorkspaceUser.WORKSPACE_NO, TWorkspace.WORKSPACE_NO)
        conds.equal(TWorkspaceUser.USER_NO, req.userNo)
        # 查询团队和个人空间
        workspace_filter = TWorkspace.filter(*conds).order_by(TWorkspace.CREATED_TIME.desc())
        # 查询公共空间
        public_workspace_filter = TWorkspace.filter(
            TWorkspace.WORKSPACE_SCOPE == 'PUBLIC',
            TWorkspace.DELETED == 0
        ).order_by(
            TWorkspace.CREATED_TIME.desc()
        )
        workspaces = workspace_filter.union(public_workspace_filter).all()

    result = []
    for workspace in workspaces:
        result.append({
            'workspaceNo': workspace.WORKSPACE_NO,
            'workspaceName': workspace.WORKSPACE_NAME,
            'workspaceScope': workspace.WORKSPACE_SCOPE,
            'workspaceDesc': workspace.WORKSPACE_DESC
        })
    return result


@http_service
def query_workspace_info(req):
    # 查询工作空间
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')
    return {
        'workspaceNo': workspace.WORKSPACE_NO,
        'workspaceName': workspace.WORKSPACE_NAME,
        'workspaceScope': workspace.WORKSPACE_SCOPE,
        'workspaceDesc': workspace.WORKSPACE_DESC
    }


@http_service
@transactional
def create_workspace(req):
    # 名称唯一性校验
    workspace = WorkspaceDao.select_by_name(req.workspaceName)
    check_not_exists(workspace, error_msg='工作空间已存在')

    # 新增空间
    workspace_no = new_id()
    TWorkspace.insert(
        WORKSPACE_NO=workspace_no,
        WORKSPACE_NAME=req.workspaceName,
        WORKSPACE_SCOPE=req.workspaceScope,
        WORKSPACE_DESC=req.workspaceDesc
    )

    # 管理员自动加入团队空间
    if req.workspaceScope == WorkspaceScope.PROTECTED.value:
        TWorkspaceUser.insert(
            WORKSPACE_NO=workspace_no,
            USER_NO=get_super_admin_userno()
        )


@http_service
@transactional
def modify_workspace(req):
    # 查询工作空间
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')
    # 更新空间信息
    workspace.update(
        WORKSPACE_NAME=req.workspaceName,
        WORKSPACE_SCOPE=req.workspaceScope,
        WORKSPACE_DESC=req.workspaceDesc
    )


@http_service
@transactional
def remove_workspace(req):
    # 查询工作空间
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')

    # 私人空间随用户，删除用户时才会删除私人空间
    if req.workspaceScope == WorkspaceScope.PRIVATE.value:
        raise ServiceError('私人空间不允许删除')
    # 团队空间有成员时不允许删除
    if (
            req.workspaceScope == WorkspaceScope.PROTECTED.value
            and WorkspaceUserDao.count_by_workspace(req.workspaceNo) != 0
    ):
        raise ServiceError('存在成员的团队空间不允许删除')

    # 删除空间限制
    restrictions = WorkspaceRestrictionDao.select_all_by_workspace(req.workspaceNo)
    for restriction in restrictions:
        # 删除豁免成员
        WorkspaceRestrictedExemptionDao.delete_all_by_restriction(restriction.RESTRICTION_NO)
        # 删除限制
        restriction.delete()

    # 删除空间
    workspace.delete()


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
