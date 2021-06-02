#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_access_token_dao.py
# @Time    : 2021/6/2 18:08
# @Author  : Kelvin.Ye
from app.user.model import TUserAccessToken


def select_by_userno(userno):
    return TUserAccessToken.query_by(USER_NO=userno).first()
