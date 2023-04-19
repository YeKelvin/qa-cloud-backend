#!/usr/bin/ python3
# @File    : test_collection_result_dao.py
# @Time    : 2021-09-17 11:23:15
# @Author  : Kelvin.Ye
import decimal
from typing import List

from app.script.model import TTestCollectionResult


def select_by_report_and_collectionno(report_no, collection_no) -> TTestCollectionResult:
    return TTestCollectionResult.filter_by(REPORT_NO=report_no, COLLECTION_NO=collection_no).first()


def select_first_by_collectionid(collection_id) -> TTestCollectionResult:
    return TTestCollectionResult.filter_by(COLLECTION_ID=collection_id).first()


def select_all_by_report(report_no) -> List[TTestCollectionResult]:
    return TTestCollectionResult.filter_by(REPORT_NO=report_no).all()


def count_by_report_and_success(report_no, success) -> int:
    return TTestCollectionResult.count_by(REPORT_NO=report_no, SUCCESS=success)


def avg_elapsed_time_by_report(report_no) -> int:
    return int(TTestCollectionResult.avg_by(TTestCollectionResult.ELAPSED_TIME, REPORT_NO=report_no))
