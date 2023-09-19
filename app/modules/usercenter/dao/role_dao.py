#!/usr/bin/ python3
# @File    : role_dao.py
# @Time    : 2021-09-23 23:48:02
# @Author  : Kelvin.Ye
from app.modules.usercenter.model import TRole


def select_by_no(role_no) -> TRole:
    return TRole.filter_by(ROLE_NO=role_no).first()


def select_by_name(role_name) -> TRole:
    return TRole.filter_by(ROLE_NAME=role_name).first()


def select_by_code(role_code) -> TRole:
    return TRole.filter_by(ROLE_CODE=role_code).first()


def select_by_name_and_code(role_name, role_code) -> TRole:
    return TRole.filter_by(ROLE_NAME=role_name, ROLE_CODE=role_code).first()


def select_all() -> list[TRole]:
    return TRole.filter_by().order_by(TRole.CREATED_TIME.desc()).all()
