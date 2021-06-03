#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_access_token_dao.py
# @Time    : 2021/6/2 18:08
# @Author  : Kelvin.Ye
from app.user.model import TRole


def select_by_roleno(role_no) -> TRole:
    return TRole.query_by(ROLE_NO=role_no).first()
