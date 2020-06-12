#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : security_route
# @Time    : 2020/6/12 18:24
# @Author  : Kelvin.Ye
from server.user.routes import blueprint
from server.user.services import security_service as service
from server.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/encryption/factor', methods=['GET'])
def create_rsa_public_key():
    """获取加密因子
    """
    return service.create_rsa_public_key()
