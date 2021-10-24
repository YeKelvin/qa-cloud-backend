#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_execution_settings_dao.py
# @Time    : 2021-09-09 20:01:12
# @Author  : Kelvin.Ye
from app.script.model import TTestplanExecutionSettings


def select_by_no(execution_no) -> TTestplanExecutionSettings:
    return TTestplanExecutionSettings.filter_by(EXECUTION_NO=execution_no).first()
