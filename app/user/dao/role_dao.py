#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_access_token_dao.py
# @Time    : 2021/6/2 18:08
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.user.model import TRole
from app.utils.sqlalchemy_util import QueryCondition


def select_by_roleno(role_no) -> TRole:
    return TRole.query_by(ROLE_NO=role_no).first()


def select_by_rolename(role_name) -> TRole:
    return TRole.query_by(ROLE_NAME=role_name).first()


def select_all() -> List[TRole]:
    return TRole.query_by().order_by(TRole.CREATED_TIME.desc()).all()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition(TRole)
    if kwargs:
        conds.add_fuzzy_match(TRole.ROLE_NO, kwargs.pop('roleNo', None))
        conds.add_fuzzy_match(TRole.ROLE_NAME, kwargs.pop('roleName', None))
        conds.add_fuzzy_match(TRole.ROLE_DESC, kwargs.pop('roleDesc', None))
        conds.add_fuzzy_match(TRole.STATE, kwargs.pop('state', None))

    page = kwargs.pop('page')
    pageSize = kwargs.pop('pageSize')

    return TRole.query.filter(*conds).order_by(TRole.CREATED_TIME.desc()).paginate(page, pageSize)
