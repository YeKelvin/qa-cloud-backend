#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_settings_dao.py
# @Time    : 2022/12/13 16:28
# @Author  : Kelvin.Ye
from app.usercenter.model import TUserSettings


def select_by_user(user_no) -> TUserSettings:
    return TUserSettings.filter_by(USER_NO=user_no).first()
