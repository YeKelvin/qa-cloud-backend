#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_service
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from datetime import datetime

from server.common.number_generator import generate_user_no
from server.librarys.decorators.service import http_service
from server.librarys.exception import ServiceError
from server.librarys.helpers.global_helper import Global
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.verify import Verify
from server.user.model import TUser, TUserRoleRel, TRole
from server.user.utils.auth import Auth
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def login(req: RequestDTO):
    user = TUser.query.filter_by(username=req.attr.username).first()
    Verify.not_empty(user, '账号或密码不正确')

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
    user.update(
        access_token=token,
        last_login_time=login_time,
        last_success_time=login_time,
        error_times=0
    )
    # 记录操作员，用于记录操作日志表
    Global.set('operator', user.username)
    return {'accessToken': token}


@http_service
def logout():
    user = Global.user_no
    user.access_token = ''
    user.updated_by = user.username
    user.save()
    return None


@http_service
def register(req: RequestDTO):
    user = TUser.query.filter_by(username=req.attr.username).first()
    Verify.empty(user, '该用户名称已存在')

    # 创建用户
    user_no = generate_user_no()
    TUser.create(
        user_no=user_no,
        username=req.attr.username,
        nickname=req.attr.nickname,
        password=req.attr.password,
        mobile_no=req.attr.mobileNo,
        email=req.attr.email,
        state='NORMAL',
        error_times=0,
        created_time=datetime.now(),
        created_by=Global.operator,
        updated_time=datetime.now(),
        updated_by=Global.operator
    )
    return None


@http_service
def reset_password(req: RequestDTO):
    user = TUser.query.filter_by(user_no=req.attr.userNo).first()
    Verify.not_empty(user, '用户不存在')

    user.password = '123456'
    user.save()
    return None


@http_service
def query_user_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    if req.attr.userNo:
        conditions.append(TUser.user_no == req.attr.userNo)
    if req.attr.username:
        conditions.append(TUser.username.like(f'%{req.attr.username}%'))
    if req.attr.nickname:
        conditions.append(TUser.nickname.like(f'%{req.attr.nickname}%'))
    if req.attr.mobileNo:
        conditions.append(TUser.mobile_no.like(f'%{req.attr.mobileNo}%'))
    if req.attr.email:
        conditions.append(TUser.email.like(f'%{req.attr.email}%'))
    if req.attr.state:
        conditions.append(TUser.state.like(f'%{req.attr.state}%'))

    # 列表总数
    total_size = TUser.query.filter(*conditions).count()
    # 列表数据
    users = TUser.query.filter(*conditions).order_by(TUser.created_time.desc()).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for user in users:
        user_roles = TUserRoleRel.query.filter_by(user_no=user.user_no).all()
        roles = []
        for user_role in user_roles:
            role = TRole.query.filter_by(role_no=user_role.role_no).first()
            roles.append(role.role_name)
        data_set.append({
            'userNo': user.user_no,
            'username': user.username,
            'nickname': user.nickname,
            'mobileNo': user.mobile_no,
            'email': user.email,
            'state': user.state,
            'roles': roles
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def query_user_all():
    users = TUser.query.order_by(TUser.created_time.desc()).all()
    result = []
    for user in users:
        result.append({
            'userNo': user.user_no,
            'username': user.username
        })
    return result


@http_service
def query_user_info():
    user = Global.user_no
    user_roles = TUserRoleRel.query.filter_by(user_no=user.user_no).all()
    roles = []
    for user_role in user_roles:
        role = TRole.query.filter_by(role_no=user_role.role_no).first()
        roles.append(role.role_name)
    return {
        'userNo': user.user_no,
        'username': user.username,
        'nickname': user.nickname,
        'mobileNo': user.mobile_no,
        'email': user.email,
        'avatar': user.avatar,
        'roles': roles
    }


@http_service
def modify_user(req: RequestDTO):
    user = TUser.query.filter_by(user_no=req.attr.userNo).first()
    Verify.not_empty(user, '用户不存在')

    if req.attr.nickname is not None:
        user.nickname = req.attr.nickname
    if req.attr.mobileNo is not None:
        user.mobile_no = req.attr.mobileNo
    if req.attr.email is not None:
        user.email = req.attr.email

    user.save()
    return None


@http_service
def modify_user_state(req: RequestDTO):
    user = TUser.query.filter_by(user_no=req.attr.userNo).first()
    Verify.not_empty(user, '用户不存在')

    user.update(state=req.attr.state)
    return None


@http_service
def delete_user(req: RequestDTO):
    user = TUser.query.filter_by(user_no=req.attr.userNo).first()
    Verify.not_empty(user, '用户不存在')

    # 删除用户角色关联关系
    user_roles = TUserRoleRel.query.filter_by(user_no=req.attr.userNo).all()
    for user_role in user_roles:
        user_role.delete()

    # 删除用户
    user.delete()
    return None
