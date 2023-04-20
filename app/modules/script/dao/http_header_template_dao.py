#!/usr/bin/ python3
# @File    : http_header_template_dao.py
# @Time    : 2021-08-20 13:16:23
# @Author  : Kelvin.Ye
from app.modules.script.model import THttpHeaderTemplate


def select_by_no(template_no) -> THttpHeaderTemplate:
    return THttpHeaderTemplate.filter_by(TEMPLATE_NO=template_no).first()


def select_by_name(template_name) -> THttpHeaderTemplate:
    return THttpHeaderTemplate.filter_by(TEMPLATE_NAME=template_name).first()


def select_by_workspace_and_name(workspace_no, template_name) -> THttpHeaderTemplate:
    return THttpHeaderTemplate.filter_by(WORKSPACE_NO=workspace_no, TEMPLATE_NAME=template_name).first()
