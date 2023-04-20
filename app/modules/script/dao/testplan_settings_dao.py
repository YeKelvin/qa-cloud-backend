#!/usr/bin/ python3
# @File    : testplan_settings_dao.py
# @Time    : 2021-09-09 20:01:12
# @Author  : Kelvin.Ye
from app.modules.script.model import TTestplanSettings


def select_by_no(plan_no) -> TTestplanSettings:
    return TTestplanSettings.filter_by(PLAN_NO=plan_no).first()
