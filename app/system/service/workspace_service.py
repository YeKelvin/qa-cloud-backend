#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_service.py
# @Time    : 2019/11/14 9:51
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.id_generator import new_id
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.system.dao import workspace_dao as WorkspaceDao
from app.system.model import TWorkspace
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_workspace_list(req):
    workspaces = WorkspaceDao.select_list(
        workspaceNo=req.workspaceNo,
        workspaceName=req.workspaceName,
        workspaceType=req.workspaceType,
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
            'workspaceDesc': workspace.WORKSPACE_DESC
        })
    return result


@http_service
def create_workspace(req):
    workspace = WorkspaceDao.select_by_workspacename(req.workspaceName)
    check_is_blank(workspace, '工作空间已存在')

    TWorkspace.insert(
        WORKSPACE_NO=new_id(),
        WORKSPACE_NAME=req.workspaceName,
        WORKSPACE_TYPE=req.workspaceType,
        WORKSPACE_DESC=req.workspaceDesc
    )


@http_service
def modify_workspace(req):
    workspace = WorkspaceDao.select_by_workspaceno(req.workspaceNo)
    check_is_not_blank(workspace, '工作空间不存在')

    workspace.update(
        WORKSPACE_NAME=req.workspaceName,
        WORKSPACE_TYPE=req.workspaceType,
        WORKSPACE_DESC=req.workspaceDesc
    )


@http_service
def delete_workspace(req):
    workspace = WorkspaceDao.select_by_workspaceno(req.workspaceNo)
    check_is_not_blank(workspace, '工作空间不存在')

    workspace.delete()
