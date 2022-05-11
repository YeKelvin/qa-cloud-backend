#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : validator.py
# @Time    : 2019/11/21 15:04
# @Author  : Kelvin.Ye
import enum
import re

from flask import g
from flask import request

from app.common.exceptions import ErrorCode
from app.common.exceptions import ServiceError
from app.public.model import TWorkspaceRestrictedExemption
from app.public.model import TWorkspaceRestriction
from app.public.model import TWorkspaceUser
from app.usercenter.model import TUserGroup


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


def get_user_workspace_numbered_list(user_no) -> list:
    return [entity.WORKSPACE_NO for entity in TWorkspaceUser.filter_by(USER_NO=user_no).all()]


def get_user_group_numbered_list(user_no) -> list:
    return [entity.GROUP_NO for entity in TUserGroup.filter_by(USER_NO=user_no).all()]


def match_restriction(restriction: TWorkspaceRestriction):
    if not restriction.MATCH_TYPE or not restriction.MATCH_CONTENT:
        return True
    if restriction.MATCH_TYPE == 'ALL':
        return True
    if restriction.MATCH_TYPE == 'IN' and restriction.MATCH_CONTENT in request.path:
        return True
    if restriction.MATCH_TYPE == 'NOTIN' and restriction.MATCH_CONTENT not in request.path:
        return True
    if restriction.MATCH_TYPE == 'STARTWITH' and request.path.startswith(restriction.MATCH_CONTENT):
        return True
    if restriction.MATCH_TYPE == 'STARTWITH' and request.path.endswith(restriction.MATCH_CONTENT):
        return True
    if restriction.MATCH_TYPE == 'PATTERN' and re.search(restriction.MATCH_CONTENT, request.path, re.IGNORECASE):
        return True
    return False


def get_matched_restriction_numbered_list(workspace_no) -> list:
    restrictions = TWorkspaceRestriction.filter_by(
        WORKSPACE_NO=workspace_no,
        MATCH_METHOD=request.method,
        STATE='ENABLE'
    ).all()
    return [restriction.RESTRICTION_NO for restriction in restrictions if match_restriction(restriction)]


def get_restricted_exemption_numbered_list(restriction_numbered_list) -> list:
    exemptions = TWorkspaceRestrictedExemption.filter(
        TWorkspaceRestrictedExemption.RESTRICTION_NO.in_(restriction_numbered_list)
    ).all()
    return [exemption.EXEMPTION_NO for exemption in exemptions]


def check_workspace_permission(source_workspace_no) -> None:
    # 获取用户编号
    user_no = getattr(g, 'user_no', None)
    if user_no is None:
        raise ServiceError('空间权限不足，获取用户编号失败')

    # 判断用户是否是操作空间的成员
    user_workspace_numbered_list = get_user_workspace_numbered_list(user_no)
    if source_workspace_no not in user_workspace_numbered_list:
        raise ServiceError('空间权限不足，用户非目标空间成员')

    # 根据请求方法和请求路径，查询操作空间的限制项
    restriction_numbered_list = get_matched_restriction_numbered_list(source_workspace_no)
    if not restriction_numbered_list:
        return

    # 校验用户是否为豁免成员
    exemption_numbered_list = get_restricted_exemption_numbered_list(restriction_numbered_list)
    if user_no in exemption_numbered_list:
        return

    # 校验用户分组是否为豁免分组
    user_group_numbered_list = get_user_group_numbered_list(user_no)
    for group_no in user_group_numbered_list:
        if group_no in exemption_numbered_list:
            return

    raise ServiceError('空间权限不足')
