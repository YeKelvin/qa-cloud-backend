#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_dao.py
# @Time    : 2021/6/2 14:05
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.user.model import TUser
from app.utils.sqlalchemy_util import QueryCondition


def select_by_userno(user_no) -> TUser:
    return TUser.query_by(USER_NO=user_no).first()


def select_one(**kwargs) -> TUser:
    return TUser.select_one(**kwargs)


def select_list(**kwargs) -> Pagination:
    conditions = QueryCondition()
    conditions.add_exact_match(TUser.DEL_STATE, 0)
    if kwargs:
        conditions.add_fuzzy_match(TUser.USER_NO, kwargs.pop('userNo', None))
        conditions.add_fuzzy_match(TUser.USER_NAME, kwargs.pop('userName', None))
        conditions.add_fuzzy_match(TUser.MOBILE_NO, kwargs.pop('mobileNo', None))
        conditions.add_fuzzy_match(TUser.EMAIL, kwargs.pop('email', None))
        conditions.add_fuzzy_match(TUser.STATE, kwargs.pop('state', None))

    page = kwargs.pop('page')
    pageSize = kwargs.pop('pageSize')

    return TUser.query.filter(*conditions).order_by(TUser.CREATED_TIME.desc()).paginate(page, pageSize)


def select_all(**kwargs) -> List[TUser]:
    conditions = QueryCondition()
    conditions.add_exact_match(TUser.DEL_STATE, 0)
    if kwargs:
        conditions.add_fuzzy_match(TUser.USER_NO, kwargs.pop('userNo', None))
        conditions.add_fuzzy_match(TUser.USER_NAME, kwargs.pop('userName', None))
        conditions.add_fuzzy_match(TUser.MOBILE_NO, kwargs.pop('mobileNo', None))
        conditions.add_fuzzy_match(TUser.EMAIL, kwargs.pop('email', None))
        conditions.add_fuzzy_match(TUser.STATE, kwargs.pop('state', None))

    return TUser.query.filter(*conditions).order_by(TUser.CREATED_TIME.desc()).all()
