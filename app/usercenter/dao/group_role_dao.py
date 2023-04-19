#!/usr/bin/ python3
# @File    : group_role_dao.py
# @Time    : 2022/4/25 10:46
# @Author  : Kelvin.Ye
from typing import List

from app.usercenter.model import TGroupRole


def select_by_group(group_no) -> TGroupRole:
    return TGroupRole.filter_by(GROUP_NO=group_no).first()


def select_by_group_and_role(group_no, role_no) -> TGroupRole:
    return TGroupRole.filter_by(GROUP_NO=group_no, ROLE_NO=role_no).first()


def select_all_by_group(group_no) -> List[TGroupRole]:
    return TGroupRole.filter_by(GROUP_NO=group_no).all()


def select_all_by_role(role_no) -> List[TGroupRole]:
    return TGroupRole.filter_by(ROLE_NO=role_no).all()


def delete_all_by_group(group_no):
    TGroupRole.deletes_by(GROUP_NO=group_no)


def delete_all_by_group_and_notin_role(group_no, *role_nos) -> None:
    TGroupRole.deletes(
        TGroupRole.GROUP_NO == group_no,
        TGroupRole.ROLE_NO.notin_(*role_nos)
    )
