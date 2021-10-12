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
    return TUser.filter_by(USER_NO=user_no).first()


def select_first(**kwargs) -> TUser:
    return TUser.filter_by(**kwargs).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition()
    if kwargs:
        conds.like(TUser.USER_NO, kwargs.pop('userNo', None))
        conds.like(TUser.USER_NAME, kwargs.pop('userName', None))
        conds.like(TUser.MOBILE_NO, kwargs.pop('mobileNo', None))
        conds.like(TUser.EMAIL, kwargs.pop('email', None))
        conds.like(TUser.STATE, kwargs.pop('state', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return TUser.filter(*conds).order_by(TUser.CREATED_TIME.desc()).paginate(page, page_size)


def select_all(**kwargs) -> List[TUser]:
    conds = QueryCondition()
    if kwargs:
        conds.like(TUser.USER_NO, kwargs.pop('userNo', None))
        conds.like(TUser.USER_NAME, kwargs.pop('userName', None))
        conds.like(TUser.MOBILE_NO, kwargs.pop('mobileNo', None))
        conds.like(TUser.EMAIL, kwargs.pop('email', None))
        conds.like(TUser.STATE, kwargs.pop('state', None))

    return TUser.filter(*conds).order_by(TUser.CREATED_TIME.desc()).all()


def logout(user_no):
    TUser.filter_by(USER_NO=user_no).update({TUser.LOGGED_IN: False})
