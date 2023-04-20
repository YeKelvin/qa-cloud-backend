#!/usr/bin/ python3
# @File    : user_password_key_dao.py
# @Time    : 2021/6/2 18:07
# @Author  : Kelvin.Ye
from app.modules.usercenter.model import TUserSecretKey


def select_by_index(index):
    return TUserSecretKey.filter_by(INDEX=index).first()


def delete_by_index(index):
    TUserSecretKey.physical_delete_by(INDEX=index)
