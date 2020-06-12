#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : security_service
# @Time    : 2020/6/12 18:30
# @Author  : Kelvin.Ye
from server.librarys.decorators.service import http_service
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def create_rsa_public_key():
    ...
    return {'publicKey': ''}
