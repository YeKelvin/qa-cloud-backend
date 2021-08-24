#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_sampler_headers_rel_dao.py
# @Time    : 2021-08-21 23:00:19
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import THttpSamplerHeadersRel


def select_by_sampler_and_template(sampler_no, template_no) -> THttpSamplerHeadersRel:
    return THttpSamplerHeadersRel.query_by(SAMPLER_NO=sampler_no, TEMPLATE_NO=template_no).first()


def select_all_by_sampler(sampler_no) -> List[THttpSamplerHeadersRel]:
    return THttpSamplerHeadersRel.query_by(SAMPLER_NO=sampler_no).all()


def delete_not_in_template(*args):
    THttpSamplerHeadersRel.query.filter(
        THttpSamplerHeadersRel.TEMPLATE_NO.notin_(*args)).update({THttpSamplerHeadersRel.DEL_STATE: 1})
