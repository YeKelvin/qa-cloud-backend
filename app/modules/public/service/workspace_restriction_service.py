#!/usr/bin/ python3
# @File    : workspace_restriction_service.py
# @Time    : 2022/4/22 16:11
# @Author  : Kelvin.Ye
from app.database import dbquery
from app.modules.public.dao import workspace_dao as WorkspaceDao
from app.modules.public.dao import workspace_restriction_dao as WorkspaceRestrictionDao
from app.modules.public.dao import workspace_restriction_exemption_dao as WorkspaceRestrictionExemptionDao
from app.modules.public.model import TWorkspaceRestriction
from app.modules.public.model import TWorkspaceRestrictionExemption
from app.modules.usercenter.model import TPermission
from app.modules.usercenter.model import TPermissionModule
from app.modules.usercenter.model import TPermissionObject
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.validator import check_exists
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_workspace_restriction(req):
    exemption = WorkspaceRestrictionExemptionDao.select_by_workspace(req.workspaceNo)

    return {
        'permissionList': get_workspace_restriction_list(req.workspaceNo),
        'userNumbers': exemption.USER_NUMBERS if exemption else [],
        'groupNumbers': exemption.GROUP_NUMBERS if exemption else []
    }


@http_service
@transactional
def set_workspace_restriction(req):
    # 查询空间，判断空间是否有效
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')

    # 设置空间限制
    set_workspace_permission(req.workspaceNo, req.permissionNumbers)

    # 设置豁免成员和分组
    set_workspace_exemption(req.workspaceNo, req.userNumbers, req.groupNumbers)


def get_workspace_restriction_list(workspace_no):
    conds = QueryCondition(TPermissionModule, TPermissionObject, TPermission, TWorkspaceRestriction)
    conds.equal(TWorkspaceRestriction.WORKSPACE_NO, workspace_no)
    conds.equal(TWorkspaceRestriction.PERMISSION_NO, TPermission.PERMISSION_NO)
    conds.equal(TPermission.MODULE_NO, TPermissionModule.MODULE_NO)
    conds.equal(TPermission.OBJECT_NO, TPermissionObject.OBJECT_NO)

    resutls = (
        dbquery(
            TPermissionModule.MODULE_CODE,
            TPermissionObject.OBJECT_CODE,
            TPermission.PERMISSION_NO,
            TPermission.PERMISSION_NAME
        )
        .filter(*conds)
        .order_by(TPermissionModule.MODULE_CODE.asc(), TPermissionObject.OBJECT_CODE.asc())
        .all()
    )

    return [
        {
            'permissionNo': resutl.PERMISSION_NO,
            'permissionName': resutl.PERMISSION_NAME
        }
        for resutl in resutls
    ]


def set_workspace_permission(workspace_no, permission_numbers):
    # 设置空间限制
    for permission_no in permission_numbers:
        # 查询空间限制
        workspace_restriction = (
            WorkspaceRestrictionDao.select_by_workspace_and_permission(workspace_no, permission_no)
        )
        # 新增空间限制
        if not workspace_restriction:
            TWorkspaceRestriction.insert(WORKSPACE_NO=workspace_no, PERMISSION_NO=permission_no)

    # 删除不在请求中的空间限制
    WorkspaceRestrictionDao.delete_all_by_workspace_and_notin_permission(workspace_no, permission_numbers)


def set_workspace_exemption(workspace_no, user_numbers, group_numbers):
    if exemption := WorkspaceRestrictionExemptionDao.select_by_workspace(workspace_no):
        if user_numbers is not None:
            exemption.USER_NUMBERS = user_numbers
        if group_numbers is not None:
            exemption.GROUP_NUMBERS = group_numbers
    else:
        TWorkspaceRestrictionExemption.insert(
            WORKSPACE_NO=workspace_no,
            USER_NUMBERS=user_numbers if group_numbers is not None else [],
            GROUP_NUMBERS=group_numbers if group_numbers is not None else []
        )
