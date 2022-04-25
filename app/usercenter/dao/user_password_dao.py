#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_password_dao.py
# @Time    : 2021/6/2 18:05
# @Author  : Kelvin.Ye
from typing import List
from app.usercenter.model import TUserPassword


def select_loginpwd_by_user(user_no) -> TUserPassword:
    return TUserPassword.filter_by(USER_NO=user_no, PASSWORD_TYPE='LOGIN').first()


def select_all_by_user(user_no) -> List[TUserPassword]:
    return TUserPassword.filter_by(USER_NO=user_no).all()


def delete_all_by_user(user_no):
    TUserPassword.deletes_by(USER_NO=user_no)
