#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : headers_service.py
# @Time    : 2020/3/13 16:57
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_http_headers_template_list(req):
    pass


@http_service
def query_http_headers_template_all(req):
    pass


@http_service
def create_http_headers_template(req):
    pass


@http_service
def modify_http_headers_template(req):
    pass


@http_service
def delete_http_headers_template(req):
    pass


@http_service
def query_http_headers(req):
    pass


@http_service
def create_http_header(req):
    pass


@http_service
def modify_http_header(req):
    pass


@http_service
def delete_http_header(req):
    pass
