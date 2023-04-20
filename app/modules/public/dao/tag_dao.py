#!/usr/bin/ python3
# @File    : tag_dao.py
# @Time    : 2021-08-17 11:02:04
# @Author  : Kelvin.Ye
from typing import List

from app.modules.public.model import TTag


def select_by_no(tag_no) -> TTag:
    return TTag.filter_by(TAG_NO=tag_no).first()


def select_by_name(tag_name) -> TTag:
    return TTag.filter_by(TAG_NAME=tag_name).first()


def select_all() -> List[TTag]:
    return TTag.filter_by().order_by(TTag.CREATED_TIME.desc()).all()
