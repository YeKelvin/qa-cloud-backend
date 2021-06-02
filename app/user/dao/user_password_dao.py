#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_password_dao.py
# @Time    : 2021/6/2 18:05
# @Author  : Kelvin.Ye
from app.user.model import TUserPassword


def select_loginpwd_by_userno(userno):
    return TUserPassword.query_by(USER_NO=userno, PASSWORD_TYPE='LOGIN').first()
