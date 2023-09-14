#!/usr/bin/ python3
# @File    : database_config_dao.py
# @Time    : 2022-04-04 17:32:16
# @Author  : Kelvin.Ye
from app.modules.script.model import TDatabaseConfig


def select_by_no(db_no) -> TDatabaseConfig:
    return TDatabaseConfig.filter_by(DB_NO=db_no).first()


def select_by_name(db_name) -> TDatabaseConfig:
    return TDatabaseConfig.filter_by(DB_NAME=db_name).first()


def select_first(**kwargs) -> TDatabaseConfig:
    return TDatabaseConfig.filter_by(**kwargs).first()
