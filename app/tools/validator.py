#!/usr/bin/ python3
# @File    : validator.py
# @Time    : 2019/11/21 15:04
# @Author  : Kelvin.Ye
import enum

from flask import g

from app.modules.public.model import TWorkspaceRestriction
from app.modules.public.model import TWorkspaceRestrictionExemption
from app.modules.public.model import TWorkspaceUser
from app.modules.usercenter.model import TPermission
from app.modules.usercenter.model import TRole
from app.modules.usercenter.model import TUser
from app.modules.usercenter.model import TUserGroup
from app.modules.usercenter.model import TUserRole
from app.tools.exceptions import ErrorCode
from app.tools.exceptions import ServiceError
from app.utils.sqlalchemy_util import QueryCondition


def check_not_exists(obj: any, error_msg: str = 'validation failed', error: ErrorCode = None) -> None:
    """检查obj对象是否为空，不为空则抛异常"""
    if obj:
        raise ServiceError(error_msg, error)


def check_exists(obj: any, error_msg: str = 'validation failed', error: ErrorCode = None) -> None:
    """检查obj对象是否不为空，为空则抛异常"""
    if not obj:
        raise ServiceError(error_msg, error)


def check_is_in_enum(string: str, enumeration: enum, error_msg: str = 'validation failed', error: ErrorCode = None):
    """校验枚举"""
    if string not in enumeration.__members__:
        raise ServiceError(error_msg, error)


def get_user_workspace_numbers(user_no) -> list:
    return [entity.WORKSPACE_NO for entity in TWorkspaceUser.filter_by(USER_NO=user_no).all()]


def get_user_group_numbers(user_no) -> list:
    return [entity.GROUP_NO for entity in TUserGroup.filter_by(USER_NO=user_no).all()]


def is_super_admin(user_no):
    conds = QueryCondition(TUser, TRole, TUserRole)
    conds.equal(TRole.ROLE_CODE, 'SUPER_ADMIN')
    conds.equal(TUserRole.USER_NO, user_no)
    conds.equal(TUserRole.USER_NO, TUser.USER_NO)
    conds.equal(TUserRole.ROLE_NO, TRole.ROLE_NO)
    return bool(TUser.filter(*conds).first())


def exists_workspace_restriction(workspace_no):
    permission_code = getattr(g, 'permission_code', None)
    if not permission_code:
        return False
    conds = QueryCondition(TPermission, TWorkspaceRestriction)
    conds.equal(TPermission.PERMISSION_CODE, permission_code)
    conds.equal(TWorkspaceRestriction.WORKSPACE_NO, workspace_no)
    conds.equal(TWorkspaceRestriction.PERMISSION_NO, TPermission.PERMISSION_NO)
    return bool(TWorkspaceRestriction.filter(*conds).first())


def is_restriction_exemption_member(workspace_no, user_no):
    # 查询空间显示豁免
    exemption = TWorkspaceRestrictionExemption.filter_by(WORKSPACE_NO=workspace_no).first()
    # 校验用户是否为豁免成员
    if user_no in exemption.USER_NUMBERS:
        return True
    # 校验用户所在分组是否为豁免分组
    return any(group_no in exemption.GROUP_NUMBERS for group_no in get_user_group_numbers(user_no))


def check_workspace_permission(source_workspace_no) -> None:
    # 获取用户编号
    user_no = getattr(g, 'user_no', None)
    if user_no is None:
        raise ServiceError('空间权限校验失败，用户未登录')

    # 判断用户是否是操作空间的成员
    user_workspace_numbers = get_user_workspace_numbers(user_no)
    if source_workspace_no not in user_workspace_numbers:
        if is_super_admin(user_no):
            return
        raise ServiceError('空间权限不足，用户非目标空间成员')

    # 校验是否存在空间限制
    if not exists_workspace_restriction(source_workspace_no):
        return

    # 校验用户是否为豁免成员
    if is_restriction_exemption_member(source_workspace_no, user_no):
        return

    # 校验是否为超级管理员
    if is_super_admin(user_no):
        return

    raise ServiceError('空间权限不足')
