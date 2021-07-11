#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sampler_runtime_package_dao.py
# @Time    : 2021-07-11 21:13:56
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import TSamplerRuntimePackage


def select_all_by_samplerno(sampler_no) -> List[TSamplerRuntimePackage]:
    return TSamplerRuntimePackage.query_by(SAMPLER_NO=sampler_no).all()


def delete_all_by_samplerno(sampler_no):
    TSamplerRuntimePackage.query_by(SAMPLER_NO=sampler_no).update(DEL_STATE=1)
