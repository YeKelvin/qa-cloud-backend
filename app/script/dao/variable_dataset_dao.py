#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : variable_dataset_dao.py
# @Time    : 2021-07-15 16:22:34
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.script.model import TVariableDataset
from app.utils.sqlalchemy_util import QueryCondition


def select_by_no(set_no) -> TVariableDataset:
    return TVariableDataset.filter_by(DATASET_NO=set_no).first()


def select_first(**kwargs) -> TVariableDataset:
    return TVariableDataset.filter_by(**kwargs).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition()
    if kwargs:
        conds.like(TVariableDataset.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
        conds.like(TVariableDataset.DATASET_NO, kwargs.pop('setNo', None))
        conds.like(TVariableDataset.DATASET_NAME, kwargs.pop('setName', None))
        conds.like(TVariableDataset.DATASET_TYPE, kwargs.pop('setType', None))
        conds.like(TVariableDataset.DATASET_DESC, kwargs.pop('setDesc', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return TVariableDataset.filter(*conds).order_by(TVariableDataset.CREATED_TIME.desc()).paginate(page, page_size)


def select_list_in_set_orderby_weight(*set_no) -> List[TVariableDataset]:
    return TVariableDataset.filter(TVariableDataset.DATASET_NO.in_(set_no)).order_by(TVariableDataset.WEIGHT.asc()).all()


def select_all(**kwargs) -> List[TVariableDataset]:
    conds = QueryCondition()
    if kwargs:
        conds.like(TVariableDataset.WORKSPACE_NO, kwargs.pop('workspaceNo', None))
        conds.like(TVariableDataset.DATASET_NO, kwargs.pop('setNo', None))
        conds.like(TVariableDataset.DATASET_NAME, kwargs.pop('setName', None))
        conds.like(TVariableDataset.DATASET_TYPE, kwargs.pop('setType', None))
        conds.like(TVariableDataset.DATASET_DESC, kwargs.pop('setDesc', None))

    return TVariableDataset.filter(*conds).order_by(TVariableDataset.CREATED_TIME.desc()).all()
