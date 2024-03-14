#!/usr/bin/ python3
# @File    : test_element_dao.py
# @Time    : 2021/6/6 11:26
# @Author  : Kelvin.Ye
from sqlalchemy import select

from app.database import db_execute
from app.database import db_scalars
from app.modules.script.enum import ElementType
from app.modules.script.model import TTestElement


def select_by_no(element_no) -> TTestElement:
    return TTestElement.filter_by(ELEMENT_NO=element_no).first()


def get_root_by_number(root_no) -> TTestElement:
    return (
        TTestElement
        .filter(
            TTestElement.ELEMENT_NO==root_no,
            TTestElement.ELEMENT_TYPE.in_([ElementType.COLLECTION.value, ElementType.SNIPPET.value])
        )
        .first()
    )


def is_enabled(element_no) -> bool:
    return db_scalars(
        select(TTestElement.ENABLED)
        .where(
            TTestElement.exclude_deleted_data(),
            TTestElement.ELEMENT_NO == element_no
        )
    ).first()


def get_skiped_and_enabled(element_no) -> tuple[bool, bool]:
    entity = db_execute(
        select(
            TTestElement.SKIPED,
            TTestElement.ENABLED
        )
        .where(
            TTestElement.exclude_deleted_data(),
            TTestElement.ELEMENT_NO == element_no
        )
    ).first()
    return entity.SKIPED, entity.ENABLED
