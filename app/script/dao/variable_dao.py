#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : variable_dao.py
# @Time    : 2021-07-15 16:22:52
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TVariable


def select_by_no(var_no) -> TVariable:
    return TVariable.filter_by(VAR_NO=var_no).first()


def select_by_name(var_name) -> TVariable:
    return TVariable.filter_by(VAR_NAME=var_name).first()


def select_by_dataset_and_name(dataset_no, var_name) -> TVariable:
    return TVariable.filter_by(DATASET_NO=dataset_no, VAR_NAME=var_name).first()


def select_all_by_dataset(dataset_no) -> List[TVariable]:
    return TVariable.filter_by(DATASET_NO=dataset_no).all()


def select_list_in_dataset(*dataset_no) -> List[TVariable]:
    return TVariable.filter(TVariable.DATASET_NO.in_(*dataset_no)).all()


def delete_in_no(*args):
    TVariable.deletes(TVariable.VAR_NO.in_(*args))


def delete_all_by_dataset(dataset_no):
    TVariable.deletes_by(DATASET_NO=dataset_no)
