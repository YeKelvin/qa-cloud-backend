#!/usr/bin/ python3
# @File    : role_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from app.modules.usercenter.dao import role_dao
from app.modules.usercenter.dao import role_permission_dao
from app.modules.usercenter.dao import user_role_dao
from app.modules.usercenter.enum import RoleState
from app.modules.usercenter.model import TRole
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_role_list(req):
    # 查询角色列表
    conds = QueryCondition()
    conds.like(TRole.ROLE_NO, req.roleNo)
    conds.like(TRole.ROLE_NAME, req.roleName)
    conds.like(TRole.ROLE_CODE, req.roleCode)
    conds.like(TRole.ROLE_DESC, req.roleDesc)
    conds.like(TRole.ROLE_TYPE, req.roleType)
    conds.like(TRole.STATE, req.state)

    pagination = (
        TRole
        .filter(*conds)
        .order_by(TRole.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'roleNo': role.ROLE_NO,
            'roleName': role.ROLE_NAME,
            'roleCode': role.ROLE_CODE,
            'roleDesc': role.ROLE_DESC,
            'roleType': role.ROLE_TYPE,
            'roleRank': role.ROLE_RANK,
            'state': role.STATE
        }
        for role in pagination.items if role.ROLE_CODE != 'ADMIN'
    ]

    return {'list': data, 'total': pagination.total}


@http_service
def query_role_all():
    roles = role_dao.select_all()
    return [
        {
            'roleNo': role.ROLE_NO,
            'roleName': role.ROLE_NAME,
            'roleCode': role.ROLE_CODE,
            'roleDesc': role.ROLE_DESC,
            'roleType': role.ROLE_TYPE,
            'roleRank': role.ROLE_RANK,
            'state': role.STATE
        }
        for role in roles if role.ROLE_CODE != 'ADMIN'
    ]


@http_service
def query_role_info(req):
    # 查询角色
    role = role_dao.select_by_no(req.roleNo)
    check_exists(role, error='角色不存在')

    return {
        'roleNo': role.ROLE_NO,
        'roleName': role.ROLE_NAME,
        'roleCode': role.ROLE_CODE,
        'roleDesc': role.ROLE_DESC,
        'roleType': role.ROLE_TYPE,
        'roleRank': role.ROLE_RANK,
        'state': role.STATE
    }


@http_service
def create_role(req):
    # 唯一性校验
    if role_dao.select_by_name(req.roleName):
        raise ServiceError(msg='角色名称已存在')
    if role_dao.select_by_code(req.roleCode):
        raise ServiceError(msg='角色代码已存在')

    # 创建角色
    role_no = new_id()
    TRole.insert(
        ROLE_NO=role_no,
        ROLE_NAME=req.roleName,
        ROLE_CODE=req.roleCode,
        ROLE_RANK=req.roleRank,
        ROLE_DESC=req.roleDesc,
        ROLE_TYPE='CUSTOM',
        STATE=RoleState.ENABLE.value
    )

    return {'roleNo': role_no}


@http_service
def modify_role(req):
    # 查询角色
    role = role_dao.select_by_no(req.roleNo)
    check_exists(role, error='角色不存在')

    # 唯一性校验
    if role.ROLE_NAME != req.roleName and role_dao.select_by_name(req.roleName):
        raise ServiceError(msg='角色名称已存在')
    if role.ROLE_CODE != req.roleCode and role_dao.select_by_code(req.roleCode):
        raise ServiceError(msg='角色代码已存在')

    # 更新角色信息
    role.update(
        ROLE_NAME=req.roleName,
        ROLE_CODE=req.roleCode,
        ROLE_RANK=req.roleRank,
        ROLE_DESC=req.roleDesc
    )


@http_service
def modify_role_state(req):
    # 查询角色
    role = role_dao.select_by_no(req.roleNo)
    check_exists(role, error='角色不存在')

    # 更新角色状态
    role.update(STATE=req.state)


@http_service
def remove_role(req):
    # 查询角色
    role = role_dao.select_by_no(req.roleNo)
    check_exists(role, error='角色不存在')

    # 查询用户角色列表
    user_role_list = user_role_dao.select_all_by_roleno(req.roleNo)
    check_not_exists(user_role_list, error='角色与用户存在关联，请先解除关联')

    # 删除角色权限
    role_permission_dao.delete_by_role(req.roleNo)

    # 删除角色
    role.delete()
