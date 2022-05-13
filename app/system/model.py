#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from app.database import BaseColumn
from app.database import DBModel
from app.database import TSystemOperationLogContent  # noqa
from app.database import db


class TSystemOperationLog(DBModel, BaseColumn):
    """操作日志表"""
    __tablename__ = 'SYSTEM_OPERATION_LOG'
    LOG_NO = db.Column(db.String(64), index=True, nullable=False, comment='日志编号')
    OPERATION_METHOD = db.Column(db.String(128), comment='操作方法')
    OPERATION_ENDPOINT = db.Column(db.String(256), comment='操作路由')
