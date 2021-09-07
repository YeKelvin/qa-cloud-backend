#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : auth_controller.py
# @Time    : 2020/6/12 18:24
# @Author  : Kelvin.Ye
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.user.controller import blueprint
from app.user.service import auth_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/encryption/factor')
def create_rsa_public_key():
    """获取加密因子"""
    req = JsonParser(
        Argument('loginName', required=True, nullable=False, help='登录账号不能为空')
    ).parse()
    return service.create_rsa_public_key(req)
