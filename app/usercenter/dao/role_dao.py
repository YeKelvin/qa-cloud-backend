#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_dao.py
# @Time    : 2021-09-23 23:48:02
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.usercenter.model import TRole
from app.utils.sqlalchemy_util import QueryCondition


def select_by_no(role_no) -> TRole:
    return TRole.filter_by(ROLE_NO=role_no).first()


def select_by_name(role_name) -> TRole:
    return TRole.filter_by(ROLE_NAME=role_name).first()


def select_by_code(role_code) -> TRole:
    return TRole.filter_by(ROLE_CODE=role_code).first()


def select_by_name_and_code(role_name, role_code) -> TRole:
    return TRole.filter_by(ROLE_NAME=role_name, ROLE_CODE=role_code).first()


def select_all() -> List[TRole]:
    return TRole.filter_by().order_by(TRole.CREATED_TIME.desc()).all()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition()
    conds.like(TRole.ROLE_NO, kwargs.pop('roleNo', None))
    conds.like(TRole.ROLE_NAME, kwargs.pop('roleName', None))
    conds.like(TRole.ROLE_CODE, kwargs.pop('roleCode', None))
    conds.like(TRole.ROLE_DESC, kwargs.pop('roleDesc', None))
    conds.like(TRole.ROLE_TYPE, kwargs.pop('roleType', None))
    conds.like(TRole.STATE, kwargs.pop('state', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return TRole.filter(*conds).order_by(TRole.CREATED_TIME.desc()).paginate(page, page_size)
