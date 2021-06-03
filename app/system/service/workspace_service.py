#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_service.py
# @Time    : 2019/11/14 9:51
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.id_generator import new_id
from app.common.request import RequestDTO
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.system.model import TWorkspace
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_workspace_list(req: RequestDTO):
    # 查询条件
    conditions = [TWorkspace.DEL_STATE == 0]

    if req.workspaceNo:
        conditions.append(TWorkspace.WORKSPACE_NO.like(f'%{req.workspaceNo}%'))
    if req.workspaceName:
        conditions.append(TWorkspace.WORKSPACE_NAME.like(f'%{req.workspaceName}%'))
    if req.workspaceType:
        conditions.append(TWorkspace.WORKSPACE_TYPE.like(f'%{req.workspaceType}%'))
    if req.workspaceDesc:
        conditions.append(TWorkspace.WORKSPACE_DESC.like(f'%{req.workspaceDesc}%'))

    pagination = TWorkspace.query.filter(
        *conditions).order_by(TWorkspace.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data_set = []
    for item in pagination.items:
        data_set.append({
            'workspaceNo': item.WORKSPACE_NO,
            'workspaceName': item.WORKSPACE_NAME,
            'workspaceType': item.WORKSPACE_TYPE,
            'workspaceDesc': item.WORKSPACE_DESC
        })
    return {'dataSet': data_set, 'totalSize': pagination.total}


@http_service
def query_workspace_all():
    items = TWorkspace.query_by().order_by(TWorkspace.CREATED_TIME.desc()).all()
    result = []
    for item in items:
        result.append({
            'workspaceNo': item.WORKSPACE_NO,
            'workspaceName': item.WORKSPACE_NAME,
            'workspaceType': item.WORKSPACE_TYPE,
            'workspaceDesc': item.WORKSPACE_DESC
        })
    return result


@http_service
def create_workspace(req: RequestDTO):
    project = TWorkspace.query_by(WORKSPACE_NAME=req.workspaceName).first()
    check_is_blank(project, '工作空间已存在')

    TWorkspace.insert(
        WORKSPACE_NO=new_id(),
        WORKSPACE_NAME=req.workspaceName,
        WORKSPACE_TYPE=req.workspaceType,
        WORKSPACE_DESC=req.workspaceDesc
    )
    return None


@http_service
def modify_workspace(req: RequestDTO):
    workspace = TWorkspace.query_by(WORKSPACE_NO=req.workspaceNo).first()
    check_is_not_blank(workspace, '工作空间不存在')

    if req.workspaceName is not None:
        workspace.WORKSPACE_NAME = req.workspaceName
    if req.workspaceType is not None:
        workspace.WORKSPACE_TYPE = req.workspaceType
    if req.workspaceDesc is not None:
        workspace.WORKSPACE_DESC = req.workspaceDesc

    workspace.submit()
    return None


@http_service
def delete_workspace(req: RequestDTO):
    workspace = TWorkspace.query_by(WORKSPACE_NO=req.workspaceNo).first()
    check_is_not_blank(workspace, '工作空间不存在')

    workspace.update(DEL_STATE=1)
    return None


@http_service
def add_workspace_user(req: RequestDTO):
    pass


@http_service
def modify_workspace_user(req: RequestDTO):
    pass


@http_service
def remove_workspace_user(req: RequestDTO):
    pass
