#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2019/11/14 9:51
# @Author  : Kelvin.Ye
from server.common.number_generator import generate_no
from server.librarys.decorators.service import http_service
from server.librarys.request import RequestDTO
from server.librarys.verify import Verify
from server.script.model import TWorkspace
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_workspace_list(req: RequestDTO):
    # 查询条件
    conditions = [TWorkspace.DEL_STATE == 0]

    if req.attr.workspaceNo:
        conditions.append(TWorkspace.WORKSPACE_NO.like(f'%{req.attr.workspaceNo}%'))
    if req.attr.workspaceName:
        conditions.append(TWorkspace.WORKSPACE_NAME.like(f'%{req.attr.workspaceName}%'))
    if req.attr.workspaceType:
        conditions.append(TWorkspace.WORKSPACE_TYPE.like(f'%{req.attr.workspaceType}%'))
    if req.attr.workspaceDesc:
        conditions.append(TWorkspace.WORKSPACE_DESC.like(f'%{req.attr.workspaceDesc}%'))

    pagination = TWorkspace.query.filter(
        *conditions).order_by(TWorkspace.CREATED_TIME.desc()).paginate(req.attr.page, req.attr.pageSize)

    # 组装数据
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
    project = TWorkspace.query_by(WORKSPACE_NAME=req.attr.workspaceName).first()
    Verify.empty(project, '工作空间已存在')

    TWorkspace.create(
        WORKSPACE_NO=generate_no(),
        WORKSPACE_NAME=req.attr.workspaceName,
        WORKSPACE_TYPE=req.attr.workspaceType,
        WORKSPACE_DESC=req.attr.workspaceDesc
    )
    return None


@http_service
def modify_workspace(req: RequestDTO):
    workspace = TWorkspace.query_by(WORKSPACE_NO=req.attr.workspaceNo).first()
    Verify.not_empty(workspace, '工作空间不存在')

    if req.attr.workspaceName is not None:
        workspace.WORKSPACE_NAME = req.attr.workspaceName
    if req.attr.workspaceType is not None:
        workspace.WORKSPACE_TYPE = req.attr.workspaceType
    if req.attr.workspaceDesc is not None:
        workspace.WORKSPACE_DESC = req.attr.workspaceDesc

    workspace.save()
    return None


@http_service
def delete_workspace(req: RequestDTO):
    workspace = TWorkspace.query_by(WORKSPACE_NO=req.attr.workspaceNo).first()
    Verify.not_empty(workspace, '工作空间不存在')

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
