#!/usr/bin/ python3
# @File    : group_dao.py
# @Time    : 2021-09-23 23:48:02
# @Author  : Kelvin.Ye
from typing import List

from flask_sqlalchemy.pagination import Pagination

from app.usercenter.model import TGroup
from app.utils.sqlalchemy_util import QueryCondition


def select_by_no(group_no) -> TGroup:
    return TGroup.filter_by(GROUP_NO=group_no).first()


def select_by_name(group_name) -> TGroup:
    return TGroup.filter_by(GROUP_NAME=group_name).first()


def select_all() -> List[TGroup]:
    return TGroup.filter_by().order_by(TGroup.CREATED_TIME.desc()).all()


def select_list(**kwargs) -> Pagination:
    conds = QueryCondition()
    conds.like(TGroup.GROUP_NO, kwargs.pop('groupNo', None))
    conds.like(TGroup.GROUP_NAME, kwargs.pop('groupName', None))
    conds.like(TGroup.GROUP_DESC, kwargs.pop('groupDesc', None))
    conds.like(TGroup.STATE, kwargs.pop('state', None))

    page = kwargs.pop('page')
    page_size = kwargs.pop('pageSize')

    return TGroup.filter(*conds).order_by(TGroup.CREATED_TIME.desc()).paginate(page=page, per_page=page_size)
