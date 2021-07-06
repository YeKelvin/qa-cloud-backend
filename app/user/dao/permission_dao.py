#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_dao.py
# @Time    : 2021/6/3 23:28
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.user.model import TPermission
from app.utils.sqlalchemy_util import QueryCondition


def select_by_permissionno(permission_no) -> TPermission:
    return TPermission.query_by(PERMISSION_NO=permission_no).first()


def select_by_endpoint_and_method(endpoint, method) -> TPermission:
    return TPermission.query_by(ENDPOINT=endpoint, METHOD=method).first()


def select_list(**kwargs) -> Pagination:
    conditions = QueryCondition()
    conditions.add_exact_match(TPermission.DEL_STATE, 0)
    if kwargs:
        conditions.add_fuzzy_match(TPermission.PERMISSION_NO, kwargs.pop('permissionNo', None))
        conditions.add_fuzzy_match(TPermission.PERMISSION_NAME, kwargs.pop('permissionName', None))
        conditions.add_fuzzy_match(TPermission.PERMISSION_DESC, kwargs.pop('permissionDesc', None))
        conditions.add_fuzzy_match(TPermission.ENDPOINT, kwargs.pop('endpoint', None))
        conditions.add_fuzzy_match(TPermission.METHOD, kwargs.pop('method', None))
        conditions.add_fuzzy_match(TPermission.STATE, kwargs.pop('state', None))

    page = kwargs.pop('page')
    pageSize = kwargs.pop('pageSize')

    return TPermission.query.filter(*conditions).order_by(TPermission.CREATED_TIME.desc()).paginate(page, pageSize)


def select_all() -> List[TPermission]:
    return TPermission.query_by().order_by(TPermission.CREATED_TIME.desc()).all()
