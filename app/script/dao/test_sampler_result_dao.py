#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_sampler_result_dao.py
# @Time    : 2021-09-17 11:20:24
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TTestSamplerResult


def select_all_by_group(group_id) -> List[TTestSamplerResult]:
    return TTestSamplerResult.query_by(GROUP_ID=group_id).all()


def select_all_by_parent(parent_id) -> List[TTestSamplerResult]:
    return TTestSamplerResult.query_by(PARENT_ID=parent_id).all()
