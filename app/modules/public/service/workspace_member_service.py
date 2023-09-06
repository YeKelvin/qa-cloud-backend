#!/usr/bin/ python3
# @File    : workspace_user_service.py
# @Time    : 2021/6/5 23:39
# @Author  : Kelvin.Ye
from app.database import dbquery
from app.modules.public.dao import workspace_dao
from app.modules.public.dao import workspace_user_dao
from app.modules.public.model import TWorkspace
from app.modules.public.model import TWorkspaceUser
from app.modules.usercenter.model import TRole
from app.modules.usercenter.model import TUser
from app.modules.usercenter.model import TUserRole
from app.tools.exceptions import ServiceError
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_workspace_member_list(req):
    # 查询条件
    conds = QueryCondition(TUser, TWorkspace, TWorkspaceUser)
    conds.equal(TUser.USER_NO, TWorkspaceUser.USER_NO)
    conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceUser.WORKSPACE_NO)
    conds.like(TWorkspaceUser.WORKSPACE_NO, req.workspaceNo)

    # TUser, TWorkspace, TWorkspaceUser 连表查询
    pagination = (
        dbquery(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TUser.USER_NO,
            TUser.USER_NAME
        )
        .filter(*conds)
        .order_by(TWorkspaceUser.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'workspaceNo': item.WORKSPACE_NO,
            'workspaceName': item.WORKSPACE_NAME,
            'userNo': item.USER_NO,
            'userName': item.USER_NAME
        }
        for item in pagination.items
    ]

    return {'data': data, 'total': pagination.total}


@http_service
def query_workspace_member_all(req):
    # 查询条件
    conds = QueryCondition(TUser, TWorkspaceUser)
    conds.equal(TUser.USER_NO, TWorkspaceUser.USER_NO)
    conds.equal(TWorkspaceUser.WORKSPACE_NO, req.workspaceNo)

    # 查询全部空间成员
    workspace_user_list = dbquery(
        TUser.USER_NO,
        TUser.USER_NAME
    ).filter(*conds).order_by(TUser.CREATED_TIME.desc()).all()

    return [
        {
            'userNo': user.USER_NO,
            'userName': user.USER_NAME
        }
        for user in workspace_user_list
    ]


@http_service
def modify_workspace_member(req):
    # 查询元素
    workspace = workspace_dao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')

    # 成员列表添加超级管理用户编号
    members = req.members
    members.append(get_super_admin_userno())

    # 更新空间成员
    for user_no in members:
        # 查询空间成员
        workspace_user = workspace_user_dao.select_by_workspace_and_user(req.workspaceNo, user_no)
        if workspace_user:
            continue
        else:
            # 新增空间成员
            TWorkspaceUser.insert(WORKSPACE_NO=req.workspaceNo, USER_NO=user_no)

    # 删除不在请求中的空间成员
    workspace_user_dao.delete_all_by_workspace_and_notin_user(req.workspaceNo, members)


def get_super_admin_userno():
    # 查询条件
    conds = QueryCondition(TUser, TRole, TUserRole)
    conds.equal(TUser.USER_NO, TUserRole.USER_NO)
    conds.equal(TRole.ROLE_NO, TUserRole.ROLE_NO)
    conds.equal(TRole.ROLE_CODE, 'ADMIN')

    # 查询超级管理员的用户编号
    if result := dbquery(TUser.USER_NO).filter(*conds).first():
        return result[0]
    else:
        raise ServiceError('查询超级管理员用户失败')
