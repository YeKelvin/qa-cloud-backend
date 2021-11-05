#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_header_template_dao.py
# @Time    : 2021-08-20 13:16:23
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.script.model import THttpHeaderTemplate
from app.utils.sqlalchemy_util import QueryCondition


def select_by_no(template_no) -> THttpHeaderTemplate:
    return THttpHeaderTemplate.filter_by(TEMPLATE_NO=template_no).first()


def select_by_name(template_name) -> THttpHeaderTemplate:
    return THttpHeaderTemplate.filter_by(TEMPLATE_NAME=template_name).first()


def select_by_workspace_and_name(workspace_no, template_name) -> THttpHeaderTemplate:
    return THttpHeaderTemplate.filter_by(WORKSPACE_NO=workspace_no, TEMPLATE_NAME=template_name).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition()
    if kwargs:
        conds.like(THttpHeaderTemplate.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
        conds.like(THttpHeaderTemplate.TEMPLATE_NO, kwargs.pop('templateNo', None))
        conds.like(THttpHeaderTemplate.TEMPLATE_NAME, kwargs.pop('templateName', None))
        conds.like(THttpHeaderTemplate.TEMPLATE_DESC, kwargs.pop('templateDesc', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return THttpHeaderTemplate.filter(
        *conds).order_by(THttpHeaderTemplate.CREATED_TIME.desc()).paginate(page, page_size)


def select_all(**kwargs) -> List[THttpHeaderTemplate]:
    conds = QueryCondition()
    if kwargs:
        conds.like(THttpHeaderTemplate.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
        conds.like(THttpHeaderTemplate.TEMPLATE_NO, kwargs.pop('templateNo', None))
        conds.like(THttpHeaderTemplate.TEMPLATE_NAME, kwargs.pop('templateName', None))
        conds.like(THttpHeaderTemplate.TEMPLATE_DESC, kwargs.pop('templateDesc', None))

    return THttpHeaderTemplate.filter(*conds).order_by(THttpHeaderTemplate.CREATED_TIME.desc()).all()
