#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_group_result_dao.py
# @Time    : 2021-09-17 11:23:15
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TTestGroupResult


def select_all_by_collection(collection_id) -> List[TTestGroupResult]:
    return TTestGroupResult.query_by(COLLECTION_ID=collection_id).all()
