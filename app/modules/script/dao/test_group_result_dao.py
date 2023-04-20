#!/usr/bin/ python3
# @File    : test_group_result_dao.py
# @Time    : 2021-09-17 11:23:15
# @Author  : Kelvin.Ye
from typing import List

from app.modules.script.model import TTestGroupResult


def select_first_by_group(group_id) -> TTestGroupResult:
    return TTestGroupResult.filter_by(GROUP_ID=group_id).first()


def select_all_by_collection(collection_id) -> List[TTestGroupResult]:
    return TTestGroupResult.filter_by(COLLECTION_ID=collection_id).all()


def count_by_report_and_success(report_no, success) -> int:
    return TTestGroupResult.count_by(REPORT_NO=report_no, SUCCESS=success)


def count_by_collection_and_success(collection_id, success) -> int:
    return TTestGroupResult.count_by(COLLECTION_ID=collection_id, SUCCESS=success)


def avg_elapsed_time_by_report(report_no) -> int:
    return int(TTestGroupResult.avg_by(TTestGroupResult.ELAPSED_TIME, REPORT_NO=report_no))


def avg_elapsed_time_by_collection(collection_id) -> int:
    return int(TTestGroupResult.avg_by(TTestGroupResult.ELAPSED_TIME, COLLECTION_ID=collection_id))
