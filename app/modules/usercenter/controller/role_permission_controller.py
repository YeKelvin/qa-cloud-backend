#!/usr/bin/ python3
# @File    : role_permission_controller.py
# @Time    : 2020/7/3 15:15
# @Author  : Kelvin.Ye
from app.modules.usercenter.controller import blueprint
from app.modules.usercenter.service import role_permission_service as service
from app.tools.require import require_login
from app.tools.require import require_permission
from app.tools.parser import Argument
from app.tools.parser import JsonParser


@blueprint.get('/role/permissions')
@require_login
@require_permission('QUERY_ROLE')
def query_role_permissions():
    """查询角色全部权限"""
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空')
    ).parse()
    return service.query_role_permissions(req)


@blueprint.post('/role/permissions')
@require_login
@require_permission('MODIFY_ROLE')
def set_role_permissions():
    """设置角色权限"""
    req = JsonParser(
        Argument('roleNo', required=True, nullable=False, help='角色编号不能为空'),
        Argument('permissionNumbers', type=list)
    ).parse()
    return service.set_role_permissions(req)
