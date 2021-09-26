#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_headers_template_dao.py
# @Time    : 2021-08-20 13:16:23
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.script.model import THttpHeadersTemplate
from app.utils.sqlalchemy_util import QueryCondition


def select_by_no(template_no) -> THttpHeadersTemplate:
    return THttpHeadersTemplate.filter_by(TEMPLATE_NO=template_no).first()


def select_by_name(template_name) -> THttpHeadersTemplate:
    return THttpHeadersTemplate.filter_by(TEMPLATE_NAME=template_name).first()


def select_by_workspace_and_name(workspace_no, template_name) -> THttpHeadersTemplate:
    return THttpHeadersTemplate.filter_by(WORKSPACE_NO=workspace_no, TEMPLATE_NAME=template_name).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition(THttpHeadersTemplate)
    if kwargs:
        conds.like(THttpHeadersTemplate.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
        conds.like(THttpHeadersTemplate.TEMPLATE_NO, kwargs.pop('templateNo', None))
        conds.like(THttpHeadersTemplate.TEMPLATE_NAME, kwargs.pop('templateName', None))
        conds.like(THttpHeadersTemplate.TEMPLATE_DESC, kwargs.pop('templateDesc', None))

    page = kwargs.pop('page')
    pageSize = kwargs.pop('pageSize')

    return THttpHeadersTemplate.query.filter(*conds).order_by(THttpHeadersTemplate.CREATED_TIME.desc()).paginate(page, pageSize)


def select_all(**kwargs) -> List[THttpHeadersTemplate]:
    conds = QueryCondition(THttpHeadersTemplate)
    if kwargs:
        conds.like(THttpHeadersTemplate.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
        conds.like(THttpHeadersTemplate.TEMPLATE_NO, kwargs.pop('templateNo', None))
        conds.like(THttpHeadersTemplate.TEMPLATE_NAME, kwargs.pop('templateName', None))
        conds.like(THttpHeadersTemplate.TEMPLATE_DESC, kwargs.pop('templateDesc', None))

    return THttpHeadersTemplate.query.filter(*conds).order_by(THttpHeadersTemplate.CREATED_TIME.desc()).all()
