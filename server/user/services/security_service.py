#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : security_service
# @Time    : 2020/6/12 18:30
# @Author  : Kelvin.Ye
from server.librarys.decorators.service import http_service
from server.librarys.request import RequestDTO
from server.user.model import TUserPasswordKey
from server.utils.log_util import get_logger
from server.utils.rsa_util import generate_rsa_key

log = get_logger(__name__)


@http_service
def create_rsa_public_key(req: RequestDTO):
    rsa_public_key, rsa_private_key = generate_rsa_key()
    user_password_key = TUserPasswordKey.query.filter_by(LOGIN_NAME=req.attr.loginName, DEL_STATE=0).first()
    if user_password_key:
        user_password_key.update(
            PASSWORD_KEY=str(rsa_private_key, encoding='utf8')
        )
    else:
        TUserPasswordKey.create(
            LOGIN_NAME=req.attr.loginName,
            PASSWORD_KEY=str(rsa_private_key, encoding='utf8')
        )
    return {'publicKey': str(rsa_public_key, encoding='utf8')}
