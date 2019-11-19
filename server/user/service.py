#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
import datetime

from server.librarys.decorators import http_service
from server.librarys.exception import ServiceError
from server.librarys.request import RequestDTO
from server.librarys.sequence import Sequence
from server.user.auth import Auth
from server.user.model import TUser
from server.utils.log_util import get_logger
from server.utils.time_util import STRFTIME_FORMAT

log = get_logger(__name__)


@http_service
def register(req: RequestDTO):
    pass


@http_service
def login(req: RequestDTO):
    user = TUser.query.filter_by(username=req.attr.username).first()
    if not user:
        raise ServiceError('账号或密码不正确')

    if user.check_password_hash(req.attr.password):
        log.debug('密码校验通过')
        login_time = datetime.datetime.utcnow()
        token = Auth.encode_auth_token(user.user_no, login_time.strftime(STRFTIME_FORMAT))
        user.update(access_token=token, last_login_time=login_time, last_success_time=login_time, error_times=0)
        return {'accessToken': token}

    log.debug('密码校验失败')
    user.last_error_time = datetime.datetime.utcnow()
    if user.error_times < 3:
        user.error_times += 1
    user.save()
    raise ServiceError('账号或密码不正确')


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
