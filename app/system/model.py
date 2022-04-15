#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from app.database import BaseColumn
from app.database import DBModel
from app.database import db
from app.utils.log_util import get_logger


log = get_logger(__name__)


class TActionLog(DBModel, BaseColumn):
    """系统操作日志表"""
    __tablename__ = 'ACTION_LOG'
    ACTION_DESC = db.Column(db.String(256), comment='操作描述')
    ACTION_METHOD = db.Column(db.String(32), comment='操作方法')
    ACTION_ENDPOINT = db.Column(db.String(256), comment='操作路由')
    OLD_VALUE = db.Column(db.String(512), comment='旧值')
    NEW_VALUE = db.Column(db.String(512), comment='新值')


class TSystemOperationLog(DBModel, BaseColumn):
    """操作日志表"""
    __tablename__ = 'SYSTEM_OPERATION_LOG'
    LOG_NO = db.Column(db.String(32), index=True, nullable=False, comment='日志编号')
    OPERATOR_IP = db.Column(db.String(64), comment='IP地址')
    OPERATION_TYPE = db.Column(db.String(32), comment='操作类型(INSERT:新增, UPDATE:修改, DELETE:删除)')
    OPERATION_NAME = db.Column(db.String(128), comment='权限名称')
    OPERATION_METHOD = db.Column(db.String(128), comment='操作方法')
    OPERATION_ENDPOINT = db.Column(db.String(256), comment='操作路由')


class TSystemOperationLogContent(DBModel, BaseColumn):
    """操作日志内容表"""
    __tablename__ = 'SYSTEM_OPERATION_LOG_CONTENT'
    LOG_NO = db.Column(db.String(32), index=True, nullable=False, comment='日志编号')
    TABLE_NAME = db.Column(db.String(128), comment='列名')
    COLUMN_NAME = db.Column(db.String(128), comment='列名')
    COLUMN_VALUE = db.Column(db.Text, comment='列值')
    OLD_VALUE = db.Column(db.Text, comment='旧值')
    NEW_VALUE = db.Column(db.Text, comment='新值')
