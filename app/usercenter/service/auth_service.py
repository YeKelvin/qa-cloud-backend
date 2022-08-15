#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : auth_service.py
# @Time    : 2020/6/12 18:30
# @Author  : Kelvin.Ye
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.logger import get_logger
from app.usercenter.dao import user_password_key_dao as UserPasswordKeyDao
from app.usercenter.model import TUserPasswordKey
from app.utils.rsa_util import generate_rsa_key


log = get_logger(__name__)


@http_service
@transactional
def create_rsa_public_key(req):
    # 生成RSA的公钥和秘钥
    rsa_public_key, rsa_private_key = generate_rsa_key()

    if user_password_key := UserPasswordKeyDao.select_by_loginname(req.loginName):
        user_password_key.update(
            PASSWORD_KEY=str(rsa_private_key, encoding='utf8')
        )
    else:
        TUserPasswordKey.insert(
            LOGIN_NAME=req.loginName,
            PASSWORD_KEY=str(rsa_private_key, encoding='utf8')
        )

    return {'publicKey': str(rsa_public_key, encoding='utf8')}
