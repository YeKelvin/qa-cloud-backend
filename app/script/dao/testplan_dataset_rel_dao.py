#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_dataset_rel_dao.py
# @Time    : 2021-09-15 18:46:52
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TTestplanDatasetRel


def select_by_plan_and_dataset(plan_no, dataset_no) -> TTestplanDatasetRel:
    return TTestplanDatasetRel.filter_by(PLAN_NO=plan_no, DATASET_NO=dataset_no).first()


def select_all_by_plan(plan_no) -> List[TTestplanDatasetRel]:
    return TTestplanDatasetRel.filter_by(PLAN_NO=plan_no).all()


def delete_all_by_plan_and_not_in_dataset(plan_no, *args):
    TTestplanDatasetRel.filter(
        TTestplanDatasetRel.PLAN_NO == plan_no,
        TTestplanDatasetRel.DATASET_NO.notin_(*args)
    ).update({TTestplanDatasetRel.DEL_STATE: 1})
