#!/usr/bin/ python3
# @File    : user_login_info_dao.py
# @Time    : 2021/6/2 18:04
# @Author  : Kelvin.Ye
from app.modules.usercenter.model import TUserLoginInfo


def select_by_user(user_no) -> TUserLoginInfo:
    return TUserLoginInfo.filter_by(USER_NO=user_no).first()


def select_by_loginname(login_name) -> TUserLoginInfo:
    return TUserLoginInfo.filter_by(LOGIN_NAME=login_name).first()


def select_all_by_user(user_no) -> list[TUserLoginInfo]:
    return TUserLoginInfo.filter_by(USER_NO=user_no).all()


def delete_all_by_user(user_no):
    TUserLoginInfo.deletes_by(USER_NO=user_no)
