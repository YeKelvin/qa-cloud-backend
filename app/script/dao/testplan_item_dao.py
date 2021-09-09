#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_item_dao.py
# @Time    : 2021-09-09 19:59:21
# @Author  : Kelvin.Ye
from app.script.model import TTestPlanItem


def select_by_plan_and_collection(plan_no, collection_no) -> TTestPlanItem:
    return TTestPlanItem.query_by(PLAN_NO=plan_no, COLLECTION_NO=collection_no).first()
