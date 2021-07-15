#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : variable_dao.py
# @Time    : 2021-07-15 16:22:52
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TVariable


def select_by_varno(var_no) -> TVariable:
    return TVariable.query_by(VAR_NO=var_no).first()


def select_by_name(var_name) -> TVariable:
    return TVariable.query_by(VAR_NAME=var_name).first()


def select_list_by_setno(set_no) -> List[TVariable]:
    return TVariable.query_by(SET_NO=set_no).all()
