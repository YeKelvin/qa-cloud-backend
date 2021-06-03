#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : role_permission_rel_dao.py
# @Time    : 2021/6/3 23:28
# @Author  : Kelvin.Ye
from app.user.model import TRolePermissionRel


def delete_by_roleno(role_no):
    TRolePermissionRel.query_by(ROLE_NO=role_no).delete()
