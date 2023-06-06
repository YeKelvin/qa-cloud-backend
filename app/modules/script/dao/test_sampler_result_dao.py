#!/usr/bin/ python3
# @File    : test_sampler_result_dao.py
# @Time    : 2021-09-17 11:20:24
# @Author  : Kelvin.Ye
from typing import List

from app.database import dbquery
from app.modules.script.model import TTestSamplerResult


def select_first_by_sampler(sampler_id) -> TTestSamplerResult:
    return TTestSamplerResult.filter_by(SAMPLER_ID=sampler_id).first()


def select_all_summary_by_worker(worker_id) -> List[TTestSamplerResult]:
    return (
        dbquery(
            TTestSamplerResult.WORKER_ID,
            TTestSamplerResult.SAMPLER_ID,
            TTestSamplerResult.SAMPLER_NAME,
            TTestSamplerResult.SAMPLER_REMARK,
            TTestSamplerResult.START_TIME,
            TTestSamplerResult.END_TIME,
            TTestSamplerResult.ELAPSED_TIME,
            TTestSamplerResult.SUCCESS,
            TTestSamplerResult.RETRYING
        )
        .filter_by(WORKER_ID=worker_id, PARENT_ID=None)
        .all()
    )


def select_all_by_worker(worker_id) -> List[TTestSamplerResult]:
    return TTestSamplerResult.filter_by(WORKER_ID=worker_id).all()


def select_all_by_parent(parent_id) -> List[TTestSamplerResult]:
    return TTestSamplerResult.filter_by(PARENT_ID=parent_id).all()


def count_by_report_and_success(report_no, success) -> int:
    return TTestSamplerResult.count_by(REPORT_NO=report_no, SUCCESS=success)


def count_by_collection_and_success(collection_id, success) -> int:
    return TTestSamplerResult.count_by(COLLECTION_ID=collection_id, SUCCESS=success)


def count_by_worker_and_success(worker_id, success) -> int:
    return TTestSamplerResult.count_by(WORKER_ID=worker_id, SUCCESS=success)


def avg_elapsed_time_by_report(report_no) -> int:
    return int(TTestSamplerResult.avg_by(TTestSamplerResult.ELAPSED_TIME, REPORT_NO=report_no))


def avg_elapsed_time_by_collection(collection_id) -> int:
    return int(TTestSamplerResult.avg_by(TTestSamplerResult.ELAPSED_TIME, COLLECTION_ID=collection_id))


def avg_elapsed_time_by_worker(worker_id) -> int:
    return int(TTestSamplerResult.avg_by(TTestSamplerResult.ELAPSED_TIME, WORKER_ID=worker_id))
