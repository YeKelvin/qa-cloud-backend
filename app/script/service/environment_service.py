#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : environment_service.py
# @Time    : 2020/3/13 16:59
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_environment_variable_list(req):
    pass


@http_service
def query_environment_variable_all(req):
    pass


@http_service
def create_environment_variable(req):
    pass


@http_service
def modify_environment_variable(req):
    pass


@http_service
def delete_environment_variable(req):
    pass
