#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_login_info_dao.py
# @Time    : 2021/6/2 18:04
# @Author  : Kelvin.Ye
from app.user.model import TUserLoginInfo


def select_by_loginname(loginname) -> TUserLoginInfo:
    return TUserLoginInfo.query_by(LOGIN_NAME=loginname).first()
