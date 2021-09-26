#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_permission_rel_dao.py
# @Time    : 2021/6/3 23:28
# @Author  : Kelvin.Ye
from app.user.model import TRolePermissionRel


def select_by_roleno_and_permissionno(role_no, permission_no) -> TRolePermissionRel:
    return TRolePermissionRel.filter_by(ROLE_NO=role_no, PERMISSION_NO=permission_no).first()


def delete_by_roleno(role_no):
    TRolePermissionRel.filter_by(ROLE_NO=role_no).delete()
