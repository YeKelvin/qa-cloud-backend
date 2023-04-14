#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2023-04-11 18:18:01
# @Author  : Kelvin.Ye
from app.database import BaseColumn
from app.database import DBModel
from app.database import db


class TThirdPartyApplication(DBModel, BaseColumn):
    """第三方应用表"""
    __tablename__ = 'THIRD_PARTY_APPLICATION'
    APP_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='应用编号')
    APP_NAME = db.Column(db.String(128), nullable=False, comment='应用名称')
    APP_SECRET = db.Column(db.String(32), comment='应用密钥')


class TOpenApiLog(DBModel, BaseColumn):
    """开放接口日志表"""
    __tablename__ = 'OPEN_API_LOG'
    LOG_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='日志编号')
    APP_NO = db.Column(db.String(32), index=True, nullable=False, comment='应用编号')
    URI = db.Column(db.String(256), comment='接口路径')
    REQUEST = db.Column(db.Text, comment='接口请求')
    RESPONSE = db.Column(db.Text, comment='接口响应')
    STATUS = db.Column(db.String(16), comment='响应状态')
