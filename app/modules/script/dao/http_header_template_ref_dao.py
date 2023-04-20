#!/usr/bin/ python3
# @File    : http_header_template_ref_dao.py
# @Time    : 2021-08-21 23:00:19
# @Author  : Kelvin.Ye
from typing import List

from app.modules.script.model import THttpHeaderTemplateRef


def select_by_sampler_and_template(sampler_no, template_no) -> THttpHeaderTemplateRef:
    return THttpHeaderTemplateRef.filter_by(SAMPLER_NO=sampler_no, TEMPLATE_NO=template_no).first()


def select_all_by_sampler(sampler_no) -> List[THttpHeaderTemplateRef]:
    return THttpHeaderTemplateRef.filter_by(SAMPLER_NO=sampler_no).all()


def delete_all_by_sampler_and_notin_template(sampler_no, *template_nos):
    THttpHeaderTemplateRef.deletes(
        THttpHeaderTemplateRef.SAMPLER_NO == sampler_no,
        THttpHeaderTemplateRef.TEMPLATE_NO.notin_(*template_nos)
    )
