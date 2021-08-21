#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : headers_service.py
# @Time    : 2020/3/13 16:57
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.id_generator import new_id
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.script.dao import http_header_dao as HttpHeaderDao
from app.script.dao import http_headers_template_dao as HttpHeadersTemplateDao
from app.script.model import THttpHeader
from app.script.model import THttpHeadersTemplate
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_http_headers_template_list(req):
    # 条件分页查询
    pagination = HttpHeadersTemplateDao.select_list(
        templateNo=req.setNo,
        templateName=req.setName,
        templateDesc=req.setDesc,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for item in pagination.items:
        data.append({
            'templateNo': item.SET_NO,
            'templateName': item.SET_NAME,
            'templateDesc': item.SET_DESC
        })
    return {'data': data, 'total': pagination.total}


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
