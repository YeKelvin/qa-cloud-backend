#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_report_dao.py
# @Time    : 2021-09-09 19:57:39
# @Author  : Kelvin.Ye
from app.script.model import TTestReport


def select_by_no(report_no) -> TTestReport:
    return TTestReport.query_by(REPORT_NO=report_no).first()
