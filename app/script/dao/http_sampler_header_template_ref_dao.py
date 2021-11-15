#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_sampler_header_template_ref_dao.py
# @Time    : 2021-08-21 23:00:19
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import THttpSamplerHeaderTemplateRef


def select_by_sampler_and_template(sampler_no, template_no) -> THttpSamplerHeaderTemplateRef:
    return THttpSamplerHeaderTemplateRef.filter_by(SAMPLER_NO=sampler_no, TEMPLATE_NO=template_no).first()


def select_all_by_sampler(sampler_no) -> List[THttpSamplerHeaderTemplateRef]:
    return THttpSamplerHeaderTemplateRef.filter_by(SAMPLER_NO=sampler_no).all()


def delete_all_by_sampler_and_not_in_template(sampler_no, *args):
    THttpSamplerHeaderTemplateRef.filter(
        THttpSamplerHeaderTemplateRef.SAMPLER_NO == sampler_no,
        THttpSamplerHeaderTemplateRef.TEMPLATE_NO.notin_(*args)
    ).update({THttpSamplerHeaderTemplateRef.DELETED: 1})
