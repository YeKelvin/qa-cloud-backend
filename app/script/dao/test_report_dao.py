#!/usr/bin/ python3
# @File    : test_report_dao.py
# @Time    : 2021-09-09 19:57:39
# @Author  : Kelvin.Ye
from app.script.model import TTestReport


def select_by_no(report_no) -> TTestReport:
    return TTestReport.filter_by(REPORT_NO=report_no).first()


def select_by_plan(plan_no) -> TTestReport:
    return TTestReport.filter_by(PLAN_NO=plan_no).first()


def select_by_execution(execution_no) -> TTestReport:
    return TTestReport.filter_by(EXECUTION_NO=execution_no).first()
