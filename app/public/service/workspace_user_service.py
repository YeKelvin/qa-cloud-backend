#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_user_service.py
# @Time    : 2021/6/5 23:39
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.extension import db
from app.public.dao import workspace_user_rel_dao as WorkspaceUserRelDao
from app.public.model import TWorkspace
from app.public.model import TWorkspaceUserRel
from app.user.model import TUser
from app.utils.log_util import get_logger
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_workspace_user_list(req):
    # 查询条件
    conds = QueryCondition(TUser, TWorkspace, TWorkspaceUserRel)
    conds.exact_match(TUser.USER_NO, TWorkspaceUserRel.USER_NO)
    conds.exact_match(TWorkspace.WORKSPACE_NO, TWorkspaceUserRel.WORKSPACE_NO)
    conds.fuzzy_match(TWorkspaceUserRel.WORKSPACE_NO, req.workspaceNo)

    # TUser, TWorkspace, TWorkspaceUserRel 连表查询
    pagination = db.session.query(
        TWorkspace.WORKSPACE_NO,
        TWorkspace.WORKSPACE_NAME,
        TUser.USER_NO,
        TUser.USER_NAME
    ).filter(*conds).order_by(TWorkspaceUserRel.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

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
def create_workspace_user(req):
    # 查询空间用户
    workspace_user = WorkspaceUserRelDao.select_by_workspace_and_user(req.workspaceNo, req.userNo)
    check_is_blank(workspace_user, '空间用户关联已存在')

    # 新增空间用户
    TWorkspaceUserRel.insert(WORKSPACE_NO=req.workspaceNo, USER_NO=req.userNo)


@http_service
def remove_workspace_user(req):
    # 查询用户角色
    workspace_user = WorkspaceUserRelDao.select_by_workspace_and_user(req.workspaceNo, req.userNo)
    check_is_not_blank(workspace_user, '空间用户关联不存在')

    # 删除空间用户
    workspace_user.delete()
