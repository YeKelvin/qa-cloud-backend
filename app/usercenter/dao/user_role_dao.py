#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_role_dao.py
# @Time    : 2021/6/3 13:01
# @Author  : Kelvin.Ye
from typing import List

from app.usercenter.model import TUserRole


def select_by_userno(user_no) -> TUserRole:
    return TUserRole.filter_by(USER_NO=user_no).first()


def select_by_user_and_role(user_no, role_no) -> TUserRole:
    return TUserRole.filter_by(USER_NO=user_no, ROLE_NO=role_no).first()


def select_all_by_userno(user_no) -> List[TUserRole]:
    return TUserRole.filter_by(USER_NO=user_no).all()


def select_all_by_roleno(role_no) -> List[TUserRole]:
    return TUserRole.filter_by(ROLE_NO=role_no).all()


def delete_all_by_userno(user_no):
    entities = TUserRole.filter_by(USER_NO=user_no).all()
    for entity in entities:
        entity.delete()


def delete_all_by_user_and_notin_role(user_no, *role_number_list) -> None:
    TUserRole.filter(
        TUserRole.USER_NO == user_no,
        TUserRole.ROLE_NO.notin_(*role_number_list)
    ).update({TUserRole.DELETED: 1})
