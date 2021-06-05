#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : auth_service.py
# @Time    : 2020/6/12 18:30
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.user.dao import user_password_key_dao as UserPasswordKeyDao
from app.user.model import TUserPasswordKey
from app.utils.log_util import get_logger
from app.utils.rsa_util import generate_rsa_key


log = get_logger(__name__)


@http_service
def create_rsa_public_key(req):
    rsa_public_key, rsa_private_key = generate_rsa_key()
    user_password_key = UserPasswordKeyDao.select_by_loginname(req.loginName)
    if user_password_key:
        user_password_key.update(
            PASSWORD_KEY=str(rsa_private_key, encoding='utf8')
        )
    else:
        TUserPasswordKey.insert(
            LOGIN_NAME=req.loginName,
            PASSWORD_KEY=str(rsa_private_key, encoding='utf8')
        )

    return {'publicKey': str(rsa_public_key, encoding='utf8')}
