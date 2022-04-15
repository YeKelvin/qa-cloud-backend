#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : http_header_dao.py
# @Time    : 2021-08-20 13:16:20
# @Author  : Kelvin.Ye
from typing import List

from app.script.model import THttpHeader


def select_by_no(header_no) -> THttpHeader:
    return THttpHeader.filter_by(HEADER_NO=header_no).first()


def select_by_name(header_name) -> THttpHeader:
    return THttpHeader.filter_by(HEADER_NAME=header_name).first()


def select_by_template_and_name(template_no, header_name) -> THttpHeader:
    return THttpHeader.filter_by(TEMPLATE_NO=template_no, HEADER_NAME=header_name).first()


def select_all_by_template(template_no) -> List[THttpHeader]:
    return THttpHeader.filter_by(TEMPLATE_NO=template_no).all()


def delete_in_no(*args):
    THttpHeader.deletes(THttpHeader.HEADER_NO.in_(*args))


def delete_all_by_template(template_no):
    THttpHeader.deletes_by(TEMPLATE_NO=template_no)
