#!/usr/bin/ python3
# @File    : test_element_dao.py
# @Time    : 2021/6/6 11:26
# @Author  : Kelvin.Ye
from sqlalchemy import select

from app.database import db_scalars
from app.modules.script.model import TTestElement


def select_by_no(element_no) -> TTestElement:
    return TTestElement.filter_by(ELEMENT_NO=element_no).first()


def is_enabled(element_no) -> bool:
    return db_scalars(
        select(TTestElement.ENABLED)
        .where(
            TTestElement.exclude_deleted_data(),
            TTestElement.ELEMENT_NO == element_no
        )
    ).first()
