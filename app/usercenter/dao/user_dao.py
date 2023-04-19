#!/usr/bin/ python3
# @File    : user_dao.py
# @Time    : 2021/6/2 14:05
# @Author  : Kelvin.Ye
from app.usercenter.model import TUser


def select_by_no(user_no) -> TUser:
    return TUser.filter_by(USER_NO=user_no).first()


def select_first(**kwargs) -> TUser:
    return TUser.filter_by(**kwargs).first()
