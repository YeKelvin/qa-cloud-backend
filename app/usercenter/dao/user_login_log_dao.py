#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_login_log_dao.py
# @Time    : 2021/6/3 14:17
# @Author  : Kelvin.Ye
from typing import List
from app.usercenter.model import TUserLoginLog


def select_all_by_user(user_no) -> List[TUserLoginLog]:
    return TUserLoginLog.filter_by(USER_NO=user_no).all()


def delete_all_by_user(user_no):
    TUserLoginLog.deletes_by(USER_NO=user_no)
