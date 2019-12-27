#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from datetime import datetime

from flask import g

from server.librarys.decorators import http_service
from server.librarys.exception import ServiceError
from server.librarys.request import RequestDTO
from server.librarys.sequence import Sequence
from server.librarys.verify import Verify
from server.user.auth import Auth
from server.user.model import TUser, TUserRoleRel, TRole, TRoleMenuRel, TMenu
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def register(req: RequestDTO):
    user = TUser.query.filter_by(username=req.attr.username).first()
    Verify.is_empty(user, '该用户名称已存在')

    TUser.create(
        user_no=generate_user_no(),
        username=req.attr.username,
        nickname=req.attr.nickname,
        password=req.attr.password,
        mobile_no=req.attr.mobileNo,
        email=req.attr.email,
        state='NORMAL',
        created_time=datetime.now(),
        created_by=getattr(g, 'operator', None),
        updated_by=getattr(g, 'operator', None)
    )


@http_service
def login(req: RequestDTO):
    user = TUser.query.filter_by(username=req.attr.username).first()
    Verify.is_not_empty(user, '账号或密码不正确')

    # 密码校验失败
    if not user.check_password_hash(req.attr.password):
        user.last_error_time = datetime.utcnow()
        if user.error_times < 3:
            user.error_times += 1
        user.save()
        raise ServiceError('账号或密码不正确')

    # 密码校验通过
    login_time = datetime.utcnow()
    token = Auth.encode_auth_token(user.user_no, login_time.timestamp())
    user.update(access_token=token, last_login_time=login_time, last_success_time=login_time, error_times=0)
    # 记录操作员，用于记录操作日志表
    g.operator = user.username
    return {'accessToken': token}


@http_service
def logout():
    user = getattr(g, 'user', None)
    user.access_token = ''
    user.updated_by = user.username
    return None


@http_service
def info():
    user = getattr(g, 'user', None)
    user_role = TUserRoleRel.query.filter_by(user_no=user.user_no).first()
    role = TRole.query.filter_by(role_no=user_role.role_no).first()
    return {
        'userNo': user.user_no,
        'userName': user.username,
        'nickName': user.nickname,
        'mobileNo': user.mobile_no,
        'email': user.email,
        'avatar': user.avatar,
        'roleName': role.role_name or None
    }


@http_service
def menus():
    user = getattr(g, 'user', None)
    user_role = TUserRoleRel.query.filter_by(user_no=user.user_no).first()
    Verify.is_not_empty(user_role, '查询用户菜单失败')
    role_menu_list = TRoleMenuRel.query.filter_by(role_no=user_role.role_no).all()
    Verify.is_not_empty(role_menu_list, '查询用户菜单失败')
    menus = []
    for rm in role_menu_list:
        menu = TMenu.query.filter_by(menu_no=rm.menu_no).first()
        if not menu or menu.state != 'NORMAL':
            continue
        menus.append({
            'menu_name': menu.menu_name,
            'level': menu.level,
            'order': menu.order,
            'parentNo': menu.parent_no,
            'href': menu.href,
            'icon': menu.icon
        })
    return menus


@http_service
def info_list(req: RequestDTO):
    # 查询总数
    total_size = TUser.query.count()
    offset = (int(req.attr.page) - 1) * int(req.attr.pageCount)
    limit = int(req.attr.pageCount)
    users = TUser.query.filter_by(
        user_no=req.attr.userNo,
        username=req.attr.userName,
        nickname=req.attr.nickName,
        mobile_no=req.attr.mobileNo,
        email=req.attr.email,
        state=req.attr.state,
    ).order_by(TUser.created_time.desc()).offset(offset).limit(limit).all()
    data_set = []
    for user in users:
        user_role = TUserRoleRel.query.filter_by(user_no=user.user_no).first()
        role = TRole.query.filter_by(role_no=user_role.role_no).first()
        data_set.append({
            'userNo': user.user_no,
            'userName': user.username,
            'nickName': user.nickname,
            'mobileNo': user.mobile_no,
            'email': user.email,
            'state': user.state,
            'roleName': role.role_name or None
        })
    return {'dataSet': data_set, 'totalSize': total_size}


def generate_user_no():
    """生成用户编号
    """
    seq_user_no = Sequence('seq_user_no')
    return 'U' + str(seq_user_no.next_value()).zfill(8)


def generate_role_no():
    """生成角色编号
    """
    seq_role_no = Sequence('seq_role_no')
    return 'R' + str(seq_role_no.next_value()).zfill(8)


def generate_permission_no():
    """生成权限编号
    """
    seq_permission_no = Sequence('seq_permission_no')
    return 'P' + str(seq_permission_no.next_value()).zfill(8)


def generate_menu_no():
    """生成菜单编号
    """
    seq_menu_no = Sequence('seq_menu_no')
    return 'M' + str(seq_menu_no.next_value()).zfill(8)
