#!/usr/bin/ python3
# @File    : user_group_dao.py
# @Time    : 2022/4/25 10:30
# @Author  : Kelvin.Ye
from typing import List

from app.modules.usercenter.model import TUserGroup


def select_by_user(user_no) -> TUserGroup:
    return TUserGroup.filter_by(USER_NO=user_no).first()


def select_by_user_and_group(user_no, group_no) -> TUserGroup:
    return TUserGroup.filter_by(USER_NO=user_no, GROUP_NO=group_no).first()


def select_by_group_and_user(group_no, user_no) -> TUserGroup:
    return TUserGroup.filter_by(GROUP_NO=group_no, USER_NO=user_no).first()


def select_all_by_user(user_no) -> List[TUserGroup]:
    return TUserGroup.filter_by(USER_NO=user_no).all()


def select_all_by_group(group_no) -> List[TUserGroup]:
    return TUserGroup.filter_by(GROUP_NO=group_no).all()


def delete_all_by_user(user_no):
    TUserGroup.deletes_by(USER_NO=user_no)


def delete_all_by_group(group_no):
    TUserGroup.deletes_by(GROUP_NO=group_no)


def delete_all_by_user_and_notin_group(user_no, *groups) -> None:
    TUserGroup.deletes(
        TUserGroup.USER_NO == user_no,
        TUserGroup.GROUP_NO.notin_(*groups)
    )


def delete_all_by_group_and_notin_user(group_no, *users) -> None:
    TUserGroup.deletes(
        TUserGroup.GROUP_NO == group_no,
        TUserGroup.USER_NO.notin_(*users)
    )
