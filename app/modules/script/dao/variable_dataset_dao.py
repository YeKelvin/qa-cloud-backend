#!/usr/bin/ python3
# @File    : variable_dataset_dao.py
# @Time    : 2021-07-15 16:22:34
# @Author  : Kelvin.Ye
from typing import List

from app.modules.script.model import TVariableDataset


def select_by_no(dataset_no) -> TVariableDataset:
    return TVariableDataset.filter_by(DATASET_NO=dataset_no).first()


def select_by_number_with_deleted(dataset_no) -> TVariableDataset:
    return TVariableDataset.query.filter_by(DATASET_NO=dataset_no).first()


def select_first(**kwargs) -> TVariableDataset:
    return TVariableDataset.filter_by(**kwargs).first()


def select_list_in_no(*dataset_no) -> List[TVariableDataset]:
    return (
        TVariableDataset
        .filter(TVariableDataset.DATASET_NO.in_(dataset_no))
        .order_by(TVariableDataset.DATASET_WEIGHT.asc())
        .all()
    )
