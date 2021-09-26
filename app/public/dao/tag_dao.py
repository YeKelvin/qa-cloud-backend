#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : tag_dao.py
# @Time    : 2021-08-17 11:02:04
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy import Pagination

from app.public.model import TTag
from app.utils.sqlalchemy_util import QueryCondition


def select_by_no(tag_no) -> TTag:
    return TTag.query_by(TAG_NO=tag_no).first()


def select_by_name(tag_name) -> TTag:
    return TTag.query_by(TAG_NAME=tag_name).first()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition(TTag)
    if kwargs:
        conds.like(TTag.TAG_NO, kwargs.pop('tagNo', None))
        conds.like(TTag.TAG_NAME, kwargs.pop('tagName', None))
        conds.like(TTag.TAG_DESC, kwargs.pop('tagDesc', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return TTag.query.filter(*conds).order_by(TTag.CREATED_TIME.desc()).paginate(page, page_size)


def select_all() -> List[TTag]:
    return TTag.query_by().order_by(TTag.CREATED_TIME.desc()).all()
