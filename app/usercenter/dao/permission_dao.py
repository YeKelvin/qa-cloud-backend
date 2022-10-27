#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_dao.py
# @Time    : 2021/6/3 23:28
# @Author  : Kelvin.Ye
from app.usercenter.model import TPermission


def select_by_no(permission_no) -> TPermission:
    return TPermission.filter_by(PERMISSION_NO=permission_no).first()


def select_by_name(permission_name) -> TPermission:
    return TPermission.filter_by(PERMISSION_NAME=permission_name).first()
