#!/usr/bin/ python3
# @File    : third_party_application_dao.py
# @Time    : 2023-04-17 18:04:35
# @Author  : Kelvin.Ye
from app.opencenter.model import TThirdPartyApplication


def select_by_no(app_no) -> TThirdPartyApplication:
    return TThirdPartyApplication.filter_by(APP_NO=app_no).first()
