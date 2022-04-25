#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : group_user_dao.py
# @Time    : 2022/4/25 10:30
# @Author  : Kelvin.Ye
from typing import List

from app.usercenter.model import TGroupUser


def select_by_user(user_no) -> TGroupUser:
    return TGroupUser.filter_by(USER_NO=user_no).first()


def select_by_user_and_group(user_no, group_no) -> TGroupUser:
    return TGroupUser.filter_by(USER_NO=user_no, GROUP_NO=group_no).first()


def select_by_group_and_user(group_no, user_no) -> TGroupUser:
    return TGroupUser.filter_by(GROUP_NO=group_no, USER_NO=user_no).first()


def select_all_by_user(user_no) -> List[TGroupUser]:
    return TGroupUser.filter_by(USER_NO=user_no).all()


def select_all_by_group(group_no) -> List[TGroupUser]:
    return TGroupUser.filter_by(GROUP_NO=group_no).all()


def delete_all_by_user(user_no):
    TGroupUser.deletes_by(USER_NO=user_no)


def delete_all_by_group(group_no):
    TGroupUser.deletes_by(GROUP_NO=group_no)


def delete_all_by_user_and_notin_group(user_no, *group_numbered_list) -> None:
    TGroupUser.deletes(
        TGroupUser.USER_NO == user_no,
        TGroupUser.GROUP_NO.notin_(*group_numbered_list)
    )


def delete_all_by_group_and_notin_user(group_no, *user_numbered_list) -> None:
    TGroupUser.deletes(
        TGroupUser.GROUP_NO == group_no,
        TGroupUser.USER_NO.notin_(*user_numbered_list)
    )
