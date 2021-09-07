#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_service.py
# @Time    : 2019/11/14 9:51
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.id_generator import new_id
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.public.dao import workspace_dao as WorkspaceDao
from app.public.model import TWorkspace
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_workspace_list(req):
    workspaces = WorkspaceDao.select_list(
        workspaceNo=req.workspaceNo,
        workspaceName=req.workspaceName,
        workspaceType=req.workspaceType,
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
            'workspaceType': workspace.WORKSPACE_TYPE,
            'workspaceScope': workspace.WORKSPACE_SCOPE,
            'workspaceDesc': workspace.WORKSPACE_DESC
        })
    return {'data': data, 'total': workspaces.total}


@http_service
def query_workspace_all():
    workspaces = WorkspaceDao.select_all()
    result = []
    for workspace in workspaces:
        result.append({
            'workspaceNo': workspace.WORKSPACE_NO,
            'workspaceName': workspace.WORKSPACE_NAME,
            'workspaceType': workspace.WORKSPACE_TYPE,
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
        WORKSPACE_TYPE=req.workspaceType,
        WORKSPACE_SCOPE=req.workspaceScope,
        WORKSPACE_DESC=req.workspaceDesc
    )


@http_service
def modify_workspace(req):
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_is_not_blank(workspace, '工作空间不存在')

    workspace.update(
        WORKSPACE_NAME=req.workspaceName,
        WORKSPACE_TYPE=req.workspaceType,
        WORKSPACE_SCOPE=req.workspaceScope,
        WORKSPACE_DESC=req.workspaceDesc
    )


@http_service
def remove_workspace(req):
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_is_not_blank(workspace, '工作空间不存在')

    workspace.delete()
