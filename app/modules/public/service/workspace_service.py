#!/usr/bin/ python3
# @File    : workspace_service.py
# @Time    : 2019/11/14 9:51
# @Author  : Kelvin.Ye
from app.database import db_query
from app.modules.public.dao import workspace_dao
from app.modules.public.dao import workspace_user_dao
from app.modules.public.enum import WorkspaceScope
from app.modules.public.model import TWorkspace
from app.modules.public.model import TWorkspaceRestriction
from app.modules.public.model import TWorkspaceRestrictionExemption
from app.modules.public.model import TWorkspaceUser
from app.modules.script.enum import ElementClass
from app.modules.script.enum import ElementType
from app.modules.script.enum import VariableDatasetWeight
from app.modules.script.model import TTestElement
from app.modules.script.model import TVariableDataset
from app.modules.usercenter.model import TRole
from app.modules.usercenter.model import TUser
from app.modules.usercenter.model import TUserRole
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_workspace_list(req):
    conds = QueryCondition()
    conds.like(TWorkspace.WORKSPACE_NO, req.workspaceNo)
    conds.like(TWorkspace.WORKSPACE_NAME, req.workspaceName)
    conds.like(TWorkspace.WORKSPACE_SCOPE, req.workspaceScope)
    conds.like(TWorkspace.WORKSPACE_DESC, req.workspaceDesc)

    pagination = (
        TWorkspace
        .filter(*conds)
        .group_by(TWorkspace.ID, TWorkspace.WORKSPACE_SCOPE)
        .order_by(TWorkspace.WORKSPACE_SCOPE.desc(), TWorkspace.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'workspaceNo': workspace.WORKSPACE_NO,
            'workspaceName': workspace.WORKSPACE_NAME,
            'workspaceScope': workspace.WORKSPACE_SCOPE,
            'workspaceDesc': workspace.WORKSPACE_DESC
        }
        for workspace in pagination.items
    ]

    return {'list': data, 'total': pagination.total}


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
        workspace_stmt = TWorkspace.filter(*conds).order_by(TWorkspace.CREATED_TIME.desc())
        # 查询公共空间
        public_workspace_stmt = (
            TWorkspace
            .filter(TWorkspace.WORKSPACE_SCOPE == 'PUBLIC')
            .order_by(TWorkspace.CREATED_TIME.desc())
        )
        # 连表查询
        workspaces = workspace_stmt.union(public_workspace_stmt).all()

    return [
        {
            'workspaceNo': workspace.WORKSPACE_NO,
            'workspaceName': workspace.WORKSPACE_NAME,
            'workspaceScope': workspace.WORKSPACE_SCOPE,
            'workspaceDesc': workspace.WORKSPACE_DESC
        }
        for workspace in workspaces
    ]


@http_service
def query_workspace_info(req):
    # 查询工作空间
    workspace = workspace_dao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')
    return {
        'workspaceNo': workspace.WORKSPACE_NO,
        'workspaceName': workspace.WORKSPACE_NAME,
        'workspaceScope': workspace.WORKSPACE_SCOPE,
        'workspaceDesc': workspace.WORKSPACE_DESC
    }


@http_service
def create_workspace(req):
    # 名称唯一性校验
    workspace = workspace_dao.select_by_name(req.workspaceName)
    check_not_exists(workspace, error_msg='工作空间已存在')

    # 新增空间
    workspace_no = new_id()
    TWorkspace.insert(
        WORKSPACE_NO=workspace_no,
        WORKSPACE_NAME=req.workspaceName,
        WORKSPACE_DESC=req.workspaceDesc,
        WORKSPACE_SCOPE=req.workspaceScope
    )

    # 创建空间变量
    TVariableDataset.insert(
        WORKSPACE_NO=workspace_no,
        DATASET_NO=new_id(),
        DATASET_NAME='空间变量',
        DATASET_TYPE=VariableDatasetWeight.WORKSPACE.name,
        DATASET_WEIGHT=VariableDatasetWeight.WORKSPACE.value
    )

    # 创建空间元素
    TTestElement.insert(
        ELEMENT_NO=workspace_no,
        ELEMENT_NAME='空间元素',
        ELEMENT_TYPE=ElementType.WORKSPACE.value,
        ELEMENT_CLASS=ElementClass.TEST_WORKSPACE.value
    )

    # 管理员自动加入团队空间
    if req.workspaceScope == WorkspaceScope.PROTECTED.value:
        TWorkspaceUser.insert(
            WORKSPACE_NO=workspace_no,
            USER_NO=get_super_admin_userno()
        )


@http_service
def modify_workspace(req):
    # 查询工作空间
    workspace = workspace_dao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')
    # 更新空间信息
    workspace.update(
        WORKSPACE_NAME=req.workspaceName,
        WORKSPACE_DESC=req.workspaceDesc,
        WORKSPACE_SCOPE=req.workspaceScope,
    )


@http_service
def remove_workspace(req):
    # 查询工作空间
    workspace = workspace_dao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')

    # 私人空间随用户，删除用户时才会删除私人空间
    if req.workspaceScope == WorkspaceScope.PRIVATE.value:
        raise ServiceError('私人空间不允许删除')
    # 团队空间有成员时不允许删除
    if (
            req.workspaceScope == WorkspaceScope.PROTECTED.value
            and workspace_user_dao.count_by_workspace(req.workspaceNo) != 0
    ):
        raise ServiceError('存在成员的团队空间不允许删除')

    # 删除空间限制
    TWorkspaceRestriction.deletes_by(WORKSPACE_NO=req.workspaceNo)
    # 删除空间限制豁免
    TWorkspaceRestrictionExemption.deletes_by(WORKSPACE_NO=req.workspaceNo)
    # 删除空间
    workspace.delete()


def get_super_admin_userno():
    # 查询条件
    conds = QueryCondition(TUser, TRole, TUserRole)
    conds.equal(TUser.USER_NO, TUserRole.USER_NO)
    conds.equal(TRole.ROLE_NO, TUserRole.ROLE_NO)
    conds.equal(TRole.ROLE_CODE, 'ADMIN')

    # 查询超级管理员的用户编号
    if result := db_query(TUser.USER_NO).filter(*conds).first():
        return result[0]
    else:
        raise ServiceError('查询超级管理员用户失败')
