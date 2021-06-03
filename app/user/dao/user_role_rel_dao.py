#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_role_rel_dao.py
# @Time    : 2021/6/3 13:01
# @Author  : Kelvin.Ye
from typing import List
from app.user.model import TUserRoleRel


def select_by_userno(userno) -> TUserRoleRel:
    return TUserRoleRel.query_by(USER_NO=userno).first()


def select_all_by_userno(userno) -> List[TUserRoleRel]:
    return TUserRoleRel.query_by(USER_NO=userno).all()
