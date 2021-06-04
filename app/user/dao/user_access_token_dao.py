#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : user_access_token_dao.py
# @Time    : 2021/6/2 18:08
# @Author  : Kelvin.Ye
from app.user.model import TUserAccessToken


def select_by_userno(user_no) -> TUserAccessToken:
    return TUserAccessToken.query_by(USER_NO=user_no).first()


def update_state_by_userno(state, user_no):
    entity = TUserAccessToken.query_by(USER_NO=user_no).first()
    entity.STATE = state
    entity.submit()


def update_or_insert_by_userno(user_no, **kwargs):
    entity = TUserAccessToken.query_by(USER_NO=user_no).first()

    if entity:
        entity.update(**kwargs)
    else:
        TUserAccessToken.insert(
            USER_NO=user_no,
            **kwargs
        )


def delete_by_userno(user_no):
    TUserAccessToken.query_by(USER_NO=user_no).delete()
