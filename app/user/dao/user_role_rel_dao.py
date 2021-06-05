#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_role_rel_dao.py
# @Time    : 2021/6/3 13:01
# @Author  : Kelvin.Ye
from typing import List
from app.user.model import TUserRoleRel


def select_by_userno(user_no) -> TUserRoleRel:
    return TUserRoleRel.query_by(USER_NO=user_no).first()


def select_by_userno_and_roleno(user_no, role_no) -> TUserRoleRel:
    return TUserRoleRel.query_by(USER_NO=user_no, ROLE_NO=role_no).first()


def select_all_by_userno(user_no) -> List[TUserRoleRel]:
    return TUserRoleRel.query_by(USER_NO=user_no).all()


def select_all_by_roleno(role_no) -> List[TUserRoleRel]:
    return TUserRoleRel.query_by(ROLE_NO=role_no).all()


def delete_all_by_userno(user_no):
    entities = TUserRoleRel.query_by(USER_NO=user_no).all()
    for entity in entities:
        entity.delete()
