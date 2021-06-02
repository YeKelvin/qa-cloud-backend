#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_password_key_dao.py
# @Time    : 2021/6/2 18:07
# @Author  : Kelvin.Ye
from app.user.model import TUserPasswordKey


def select_by_loginname(loginname):
    return TUserPasswordKey.query_by(LOGIN_NAME=loginname).first()
