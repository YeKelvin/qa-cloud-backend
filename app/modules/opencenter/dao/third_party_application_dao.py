#!/usr/bin/ python3
# @File    : third_party_application_dao.py
# @Time    : 2023-04-17 18:04:35
# @Author  : Kelvin.Ye
from app.modules.opencenter.model import TThirdPartyApplication


def select_by_no(app_no) -> TThirdPartyApplication:
    return TThirdPartyApplication.filter_by(APP_NO=app_no).first()


def select_by_name(app_name) -> TThirdPartyApplication:
    return TThirdPartyApplication.filter_by(APP_NAME=app_name).first()


def select_by_code(app_code) -> TThirdPartyApplication:
    return TThirdPartyApplication.filter_by(APP_CODE=app_code).first()
