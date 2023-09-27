#!/usr/bin/ python3
# @File    : group_member_dao.py
# @Time    : 2022/4/25 10:30
# @Author  : Kelvin.Ye
from app.modules.usercenter.model import TGroupMember


def select_by_user(user_no) -> TGroupMember:
    return TGroupMember.filter_by(USER_NO=user_no).first()


def select_by_user_and_group(user_no, group_no) -> TGroupMember:
    return TGroupMember.filter_by(USER_NO=user_no, GROUP_NO=group_no).first()


def select_by_group_and_user(group_no, user_no) -> TGroupMember:
    return TGroupMember.filter_by(GROUP_NO=group_no, USER_NO=user_no).first()


def select_all_by_user(user_no) -> list[TGroupMember]:
    return TGroupMember.filter_by(USER_NO=user_no).all()


def select_all_by_group(group_no) -> list[TGroupMember]:
    return TGroupMember.filter_by(GROUP_NO=group_no).all()


def delete_all_by_user(user_no):
    TGroupMember.deletes_by(USER_NO=user_no)


def delete_all_by_group(group_no):
    TGroupMember.deletes_by(GROUP_NO=group_no)


def delete_all_by_user_and_notin_group(user_no, *groups) -> None:
    TGroupMember.deletes(
        TGroupMember.USER_NO == user_no,
        TGroupMember.GROUP_NO.notin_(*groups)
    )


def delete_all_by_group_and_notin_user(group_no, *users) -> None:
    TGroupMember.deletes(
        TGroupMember.GROUP_NO == group_no,
        TGroupMember.USER_NO.notin_(*users)
    )
