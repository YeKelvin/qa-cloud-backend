#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_service.py
# @Time    : 2019/11/14 9:51
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.id_generator import new_id
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.extension import db
from app.public.dao import workspace_dao as WorkspaceDao
from app.public.model import TWorkspace
from app.public.model import TWorkspaceUserRel
from app.utils.log_util import get_logger
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
    # 查询条件
    conds = QueryCondition(TWorkspace)
    if req.userNo:
        conds.equal(TWorkspaceUserRel.WORKSPACE_NO, TWorkspace.WORKSPACE_NO)
        conds.equal(TWorkspaceUserRel.USER_NO, req.userNo)

    workspaces = db.session.query(
        TWorkspace.WORKSPACE_NO,
        TWorkspace.WORKSPACE_NAME,
        TWorkspace.WORKSPACE_SCOPE,
        TWorkspace.WORKSPACE_DESC,
        TWorkspace.CREATED_TIME
    ).filter(*conds)

    if req.userNo:
        public_workspaces = db.session.query(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            TWorkspace.WORKSPACE_DESC,
            TWorkspace.CREATED_TIME
        ).filter(
            TWorkspace.WORKSPACE_SCOPE == 'PUBLIC', TWorkspace.DEL_STATE == 0
        )
        workspaces = workspaces.union(public_workspaces).filter().order_by(TWorkspace.CREATED_TIME.desc()).all()

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
def create_workspace(req):
    workspace = WorkspaceDao.select_by_name(req.workspaceName)
    check_is_blank(workspace, '工作空间已存在')

    TWorkspace.insert(
        WORKSPACE_NO=new_id(),
        WORKSPACE_NAME=req.workspaceName,
        WORKSPACE_SCOPE=req.workspaceScope,
        WORKSPACE_DESC=req.workspaceDesc
    )


@http_service
def modify_workspace(req):
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_is_not_blank(workspace, '工作空间不存在')

    workspace.update(
        WORKSPACE_NAME=req.workspaceName,
        WORKSPACE_SCOPE=req.workspaceScope,
        WORKSPACE_DESC=req.workspaceDesc
    )


@http_service
def remove_workspace(req):
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_is_not_blank(workspace, '工作空间不存在')

    workspace.delete()
