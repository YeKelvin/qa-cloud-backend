#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_permission_dao.py
# @Time    : 2021/6/3 23:28
# @Author  : Kelvin.Ye
from app.user.model import TRolePermission


def select_by_role_and_permission(role_no, permission_no) -> TRolePermission:
    return TRolePermission.filter_by(ROLE_NO=role_no, PERMISSION_NO=permission_no).first()


def delete_by_roleno(role_no):
    TRolePermission.filter_by(ROLE_NO=role_no).delete()
