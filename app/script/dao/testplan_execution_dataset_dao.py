#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : testplan_execution_dataset_dao.py
# @Time    : 2021-09-15 18:46:52
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TTestplanExecutionDataset


def select_by_execution_and_dataset(execution_no, dataset_no) -> TTestplanExecutionDataset:
    return TTestplanExecutionDataset.filter_by(EXECUTION_NO=execution_no, DATASET_NO=dataset_no).first()


def select_all_by_execution(execution_no) -> List[TTestplanExecutionDataset]:
    return TTestplanExecutionDataset.filter_by(EXECUTION_NO=execution_no).all()


def delete_all_by_execution_and_not_in_dataset(execution_no, *args):
    TTestplanExecutionDataset.filter(
        TTestplanExecutionDataset.EXECUTION_NO == execution_no,
        TTestplanExecutionDataset.DATASET_NO.notin_(*args)
    ).update({TTestplanExecutionDataset.DELETED: 1})
