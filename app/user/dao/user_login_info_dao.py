#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_login_info_dao.py
# @Time    : 2021/6/2 18:04
# @Author  : Kelvin.Ye
from typing import List
from app.user.model import TUserLoginInfo


def select_by_loginname(login_name) -> TUserLoginInfo:
    return TUserLoginInfo.filter_by(LOGIN_NAME=login_name).first()


def select_all_by_userno(user_no) -> List[TUserLoginInfo]:
    return TUserLoginInfo.filter_by(USER_NO=user_no).all()


def delete_all_by_userno(user_no):
    entities = TUserLoginInfo.filter_by(USER_NO=user_no).all()
    for entity in entities:
        entity.delete()
