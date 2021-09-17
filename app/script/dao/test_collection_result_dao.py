#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_collection_result_dao.py
# @Time    : 2021-09-17 11:23:15
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TTestCollectionResult


def select_all_by_report(report_no) -> List[TTestCollectionResult]:
    return TTestCollectionResult.query_by(REPORT_NO=report_no).all()
