#!/usr/bin/ python3
# @File    : database_config_dao.py
# @Time    : 2022-04-04 17:32:16
# @Author  : Kelvin.Ye
from app.modules.script.model import TDatabaseConfig


def select_by_no(config_no) -> TDatabaseConfig:
    return TDatabaseConfig.filter_by(CONFIG_NO=config_no).first()


def select_by_name(config_name) -> TDatabaseConfig:
    return TDatabaseConfig.filter_by(CONFIG_NAME=config_name).first()


def select_first(**kwargs) -> TDatabaseConfig:
    return TDatabaseConfig.filter_by(**kwargs).first()
