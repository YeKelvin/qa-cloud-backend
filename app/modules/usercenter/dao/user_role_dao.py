#!/usr/bin/ python3
# @File    : user_role_dao.py
# @Time    : 2021/6/3 13:01
# @Author  : Kelvin.Ye
from typing import List

from app.modules.usercenter.model import TUserRole


def select_by_userno(user_no) -> TUserRole:
    return TUserRole.filter_by(USER_NO=user_no).first()


def select_by_user_and_role(user_no, role_no) -> TUserRole:
    return TUserRole.filter_by(USER_NO=user_no, ROLE_NO=role_no).first()


def select_all_by_userno(user_no) -> List[TUserRole]:
    return TUserRole.filter_by(USER_NO=user_no).all()


def select_all_by_roleno(role_no) -> List[TUserRole]:
    return TUserRole.filter_by(ROLE_NO=role_no).all()


def delete_all_by_user(user_no):
    TUserRole.deletes_by(USER_NO=user_no)


def delete_all_by_user_and_notin_role(user_no, *roles) -> None:
    TUserRole.deletes(
        TUserRole.USER_NO == user_no,
        TUserRole.ROLE_NO.notin_(*roles)
    )
