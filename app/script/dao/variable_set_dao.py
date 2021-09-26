#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : variable_set_dao.py
# @Time    : 2021-07-15 16:22:34
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.script.model import TVariableSet
from app.utils.sqlalchemy_util import QueryCondition


def select_by_no(set_no) -> TVariableSet:
    return TVariableSet.query_by(SET_NO=set_no).first()


def select_first(**kwargs) -> TVariableSet:
    return TVariableSet.query_by(**kwargs).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition(TVariableSet)
    if kwargs:
        conds.like(TVariableSet.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
        conds.like(TVariableSet.SET_NO, kwargs.pop('setNo', None))
        conds.like(TVariableSet.SET_NAME, kwargs.pop('setName', None))
        conds.like(TVariableSet.SET_TYPE, kwargs.pop('setType', None))
        conds.like(TVariableSet.SET_DESC, kwargs.pop('setDesc', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return TVariableSet.query.filter(*conds).order_by(TVariableSet.CREATED_TIME.desc()).paginate(page, page_size)


def select_list_in_set_orderby_weight(*set_no) -> List[TVariableSet]:
    return TVariableSet.query.filter(TVariableSet.SET_NO.in_(set_no)).order_by(TVariableSet.WEIGHT.asc()).all()


def select_all(**kwargs) -> List[TVariableSet]:
    conds = QueryCondition(TVariableSet)
    if kwargs:
        conds.like(TVariableSet.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
        conds.like(TVariableSet.SET_NO, kwargs.pop('setNo', None))
        conds.like(TVariableSet.SET_NAME, kwargs.pop('setName', None))
        conds.like(TVariableSet.SET_TYPE, kwargs.pop('setType', None))
        conds.like(TVariableSet.SET_DESC, kwargs.pop('setDesc', None))

    return TVariableSet.query.filter(*conds).order_by(TVariableSet.CREATED_TIME.desc()).all()
