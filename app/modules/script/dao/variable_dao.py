#!/usr/bin/ python3
# @File    : variable_dao.py
# @Time    : 2021-07-15 16:22:52
# @Author  : Kelvin.Ye
from app.modules.script.model import TVariable


def select_by_no(variable_no) -> TVariable:
    return TVariable.filter_by(VARIABLE_NO=variable_no).first()


def select_by_name(variable_name) -> TVariable:
    return TVariable.filter_by(VARIABLE_NAME=variable_name).first()


def select_by_dataset_and_name(dataset_no, variable_name) -> TVariable:
    return TVariable.filter_by(DATASET_NO=dataset_no, VARIABLE_NAME=variable_name).first()


def select_all_by_dataset(dataset_no) -> list[TVariable]:
    return TVariable.filter_by(DATASET_NO=dataset_no).all()


def select_list_in_dataset(*dataset_no) -> list[TVariable]:
    return TVariable.filter(TVariable.DATASET_NO.in_(*dataset_no)).all()


def delete_in_no(*args):
    TVariable.deletes(TVariable.VARIABLE_NO.in_(*args))


def delete_all_by_dataset(dataset_no):
    TVariable.deletes_by(DATASET_NO=dataset_no)
