#!/usr/bin/ python3
# @File    : test_worker_result_dao.py
# @Time    : 2021-09-17 11:23:15
# @Author  : Kelvin.Ye
from app.modules.script.model import TTestWorkerResult


def select_first_by_worker(worker_id) -> TTestWorkerResult:
    return TTestWorkerResult.filter_by(WORKER_ID=worker_id).first()


def select_all_by_collection(collection_id) -> list[TTestWorkerResult]:
    return TTestWorkerResult.filter_by(COLLECTION_ID=collection_id).all()


def count_by_report_and_success(report_no, success) -> int:
    return TTestWorkerResult.count_by(REPORT_NO=report_no, SUCCESS=success)


def count_by_collection_and_success(collection_id, success) -> int:
    return TTestWorkerResult.count_by(COLLECTION_ID=collection_id, SUCCESS=success)


def avg_elapsed_time_by_report(report_no) -> int:
    return int(TTestWorkerResult.avg_by(TTestWorkerResult.ELAPSED_TIME, REPORT_NO=report_no))


def avg_elapsed_time_by_collection(collection_id) -> int:
    return int(TTestWorkerResult.avg_by(TTestWorkerResult.ELAPSED_TIME, COLLECTION_ID=collection_id))
