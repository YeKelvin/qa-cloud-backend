#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_dao.py
# @Time    : 2021/6/3 23:28
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.usercenter.model import TPermission
from app.utils.sqlalchemy_util import QueryCondition


def select_by_no(permission_no) -> TPermission:
    return TPermission.filter_by(PERMISSION_NO=permission_no).first()


def select_by_name(permission_name) -> TPermission:
    return TPermission.filter_by(PERMISSION_NAME=permission_name).first()


def select_by_endpoint_and_method(endpoint, method) -> TPermission:
    return TPermission.filter_by(ENDPOINT=endpoint, METHOD=method).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition()
    conds.like(TPermission.PERMISSION_NO, kwargs.pop('permissionNo', None))
    conds.like(TPermission.PERMISSION_NAME, kwargs.pop('permissionName', None))
    conds.like(TPermission.PERMISSION_DESC, kwargs.pop('permissionDesc', None))
    conds.like(TPermission.ENDPOINT, kwargs.pop('endpoint', None))
    conds.like(TPermission.METHOD, kwargs.pop('method', None))
    conds.like(TPermission.STATE, kwargs.pop('state', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return TPermission.filter(*conds).order_by(TPermission.CREATED_TIME.desc()).paginate(page, page_size)


def select_all() -> List[TPermission]:
    return TPermission.filter_by().order_by(TPermission.CREATED_TIME.desc()).all()
