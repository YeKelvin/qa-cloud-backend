#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_dao.py
# @Time    : 2021/6/2 14:05
# @Author  : Kelvin.Ye
from app.user.model import TUser


def select_by_userno(userno):
    return TUser.query_by(USER_NO=userno).first()
