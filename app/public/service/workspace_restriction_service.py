#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_restriction_service.py
# @Time    : 2022/4/22 16:11
# @Author  : Kelvin.Ye
from app.extension import db
from app.public.dao import workspace_dao as WorkspaceDao
from app.public.dao import workspace_restricted_exemption_dao as WorkspaceRestrictedExemptionDao
from app.public.dao import workspace_restriction_dao as WorkspaceRestrictionDao
from app.public.enum import RestrictedExemptionType
from app.public.enum import RestrictionMatchType
from app.public.model import TWorkspaceRestrictedExemption
from app.public.model import TWorkspaceRestriction
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.logger import get_logger
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.usercenter.model import TGroup
from app.usercenter.model import TUser
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_workspace_restriction_list(req):
    # 查询条件
    conds = QueryCondition(TWorkspaceRestriction)
    conds.like(TWorkspaceRestriction.WORKSPACE_NO, req.workspaceNo)
    conds.like(TWorkspaceRestriction.MATCH_METHOD, req.matchMethod)
    conds.like(TWorkspaceRestriction.MATCH_TYPE, req.matchType)
    conds.like(TWorkspaceRestriction.MATCH_CONTENT, req.matchContent)

    if req.exemptionUserName:
        conds.add_table(TUser)
        conds.add_table(TWorkspaceRestrictedExemption)
        conds.like(TUser.USER_NAME, req.exemptionUserName)
        conds.equal(TWorkspaceRestrictedExemption.EXEMPTION_NO, TUser.USER_NO)
        conds.equal(TWorkspaceRestrictedExemption.RESTRICTION_NO, TWorkspaceRestriction.RESTRICTION_NO)

    # 连表查询
    pagination = db.session.query(
        TWorkspaceRestriction
    ).filter(*conds).order_by(TWorkspaceRestriction.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for item in pagination.items:
        # 查询豁免成员
        conds = QueryCondition(TWorkspaceRestrictedExemption, TUser)
        conds.equal(TWorkspaceRestrictedExemption.RESTRICTION_NO, item.RESTRICTION_NO)
        conds.equal(TWorkspaceRestrictedExemption.EXEMPTION_TYPE, RestrictedExemptionType.USER.value)
        conds.equal(TWorkspaceRestrictedExemption.EXEMPTION_NO, TUser.USER_NO)
        user_list = db.session.query(TUser.USER_NO, TUser.USER_NAME).filter(*conds).all()
        # 查询豁免分组
        conds = QueryCondition(TWorkspaceRestrictedExemption, TGroup)
        conds.equal(TWorkspaceRestrictedExemption.RESTRICTION_NO, item.RESTRICTION_NO)
        conds.equal(TWorkspaceRestrictedExemption.EXEMPTION_TYPE, RestrictedExemptionType.GROUP.value)
        conds.equal(TWorkspaceRestrictedExemption.EXEMPTION_NO, TGroup.GROUP_NO)
        group_list = db.session.query(TGroup.GROUP_NO, TGroup.GROUP_NAME).filter(*conds).all()
        # 添加限制项
        data.append({
            'restrictionNo': item.RESTRICTION_NO,
            'matchMethod': item.MATCH_METHOD,
            'matchType': item.MATCH_TYPE,
            'matchContent': item.MATCH_CONTENT,
            'state': item.STATE,
            'exemptionUserList': [{'userNo': user.USER_NO, 'userName': user.USER_NAME} for user in user_list],
            'exemptionGroupList': [{'groupNo': group.GROUP_NO, 'groupName': group.GROUP_NAME} for group in group_list]
        })

    return {'data': data, 'total': pagination.total}


@http_service
def query_workspace_restriction_all(req):
    # 查询空间所有的限制项
    restrictions = WorkspaceRestrictionDao.select_all_by_workspace(req.workspaceNo)
    result = []
    for restriction in restrictions:
        # 添加限制项
        result.append({
            'restrictionNo': restriction.RESTRICTION_NO,
            'matchMethod': restriction.MATCH_METHOD,
            'matchType': restriction.MATCH_TYPE,
            'matchContent': restriction.MATCH_CONTENT,
            'state': restriction.STATE
        })
    return result


@http_service
@transactional
def create_workspace_restriction(req):
    if req.matchType != RestrictionMatchType.ALL.value and not req.matchContent:
        raise ServiceError('匹配类型非所有时，匹配内容不能为空')

    # 查询空间，判断空间是否有效
    workspace = WorkspaceDao.select_by_no(req.workspaceNo)
    check_exists(workspace, error_msg='工作空间不存在')

    # 查询空间限制
    restriction = WorkspaceRestrictionDao.select_first(
        WORKSPACE_NO=req.workspaceNo,
        MATCH_METHOD=req.matchMethod,
        MATCH_TYPE=req.matchType,
        MATCH_CONTENT=req.matchContent
    )
    check_not_exists(restriction, error_msg='同规则的空间限制已存在')

    # 新增空间限制
    restriction_no = new_id()
    TWorkspaceRestriction.insert(
        WORKSPACE_NO=req.workspaceNo,
        RESTRICTION_NO=restriction_no,
        MATCH_METHOD=req.matchMethod,
        MATCH_TYPE=req.matchType,
        MATCH_CONTENT=req.matchContent
    )

    # 新增豁免成员
    if req.exemptionUserNos:
        for userno in req.exemptionUserNos:
            TWorkspaceRestrictedExemption.insert(
                RESTRICTION_NO=restriction_no,
                EXEMPTION_TYPE=RestrictedExemptionType.USER.value,
                EXEMPTION_NO=userno
            )

    # 新增豁免分组
    if req.exemptionGroupNos:
        for groupno in req.exemptionGroupNos:
            TWorkspaceRestrictedExemption.insert(
                RESTRICTION_NO=restriction_no,
                EXEMPTION_TYPE=RestrictedExemptionType.GROUP.value,
                EXEMPTION_NO=groupno
            )

    return {'restrictionNo': restriction_no}


@http_service
@transactional
def modify_workspace_restriction(req):
    if req.matchType != RestrictionMatchType.ALL.value and not req.matchContent:
        raise ServiceError('匹配类型非所有时，匹配内容不能为空')

    # 查询空间限制
    restriction = WorkspaceRestrictionDao.select_by_restriction(req.restrictionNo)
    check_exists(restriction, error_msg='空间限制不存在')

    # 更新限制信息
    restriction.update(
        MATCH_METHOD=req.matchMethod,
        MATCH_TYPE=req.matchType,
        MATCH_CONTENT=req.matchContent
    )

    # 更新豁免成员列表
    if req.exemptionUserNos:
        for userno in req.exemptionUserNos:
            exemption = WorkspaceRestrictedExemptionDao.select_first(
                RESTRICTION_NO=req.restrictionNo,
                EXEMPTION_TYPE=RestrictedExemptionType.USER.value,
                EXEMPTION_NO=userno
            )
            if exemption:
                continue
            else:
                TWorkspaceRestrictedExemption.insert(
                    RESTRICTION_NO=req.restrictionNo,
                    EXEMPTION_TYPE=RestrictedExemptionType.USER.value,
                    EXEMPTION_NO=userno
                )
        # 删除不在请求中的豁免成员
        WorkspaceRestrictedExemptionDao.delete_all_by_restriction_and_notin_exemption(
            req.restrictionNo,
            RestrictedExemptionType.USER.value,
            req.exemptionUserNos
        )

    # 更新豁免分组列表
    if req.exemptionGroupNos:
        for groupno in req.exemptionGroupNos:
            exemption = WorkspaceRestrictedExemptionDao.select_first(
                RESTRICTION_NO=req.restrictionNo,
                EXEMPTION_TYPE=RestrictedExemptionType.GROUP.value,
                EXEMPTION_NO=groupno
            )
            if exemption:
                continue
            else:
                TWorkspaceRestrictedExemption.insert(
                    RESTRICTION_NO=req.restrictionNo,
                    EXEMPTION_TYPE=RestrictedExemptionType.GROUP.value,
                    EXEMPTION_NO=groupno
                )
        # 删除不在请求中的豁免分组
        WorkspaceRestrictedExemptionDao.delete_all_by_restriction_and_notin_exemption(
            req.restrictionNo,
            RestrictedExemptionType.GROUP.value,
            req.exemptionGroupNos
        )


@http_service
@transactional
def remove_workspace_restriction(req):
    # 查询空间限制
    restriction = WorkspaceRestrictionDao.select_by_restriction(req.restrictionNo)
    check_exists(restriction, error_msg='空间限制不存在')

    # 删除豁免成员
    WorkspaceRestrictedExemptionDao.delete_all_by_restriction(req.restrictionNo)

    # 删除空间限制
    restriction.delete()


@http_service
@transactional
def enable_workspace_restriction(req):
    # 查询空间限制
    restriction = WorkspaceRestrictionDao.select_by_restriction(req.restrictionNo)
    check_exists(restriction, error_msg='空间限制不存在')
    # 启用空间限制
    restriction.update(STATE='ENABLE')


@http_service
@transactional
def disable_workspace_restriction(req):
    # 查询空间限制
    restriction = WorkspaceRestrictionDao.select_by_restriction(req.restrictionNo)
    check_exists(restriction, error_msg='空间限制不存在')
    # 禁用空间限制
    restriction.update(STATE='DISABLE')
