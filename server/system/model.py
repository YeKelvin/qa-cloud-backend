#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from server.database import Model, db
from server.utils.log_util import get_logger

log = get_logger(__name__)


class TActionLog(Model):
    """系统操作日志表
    """
    __tablename__ = 't_action_log'
    id = db.Column(db.Integer, primary_key=True)
    action_detail = db.Column(db.String(256), comment='操作描述')
    action_method = db.Column(db.String(32), comment='操作方法')
    action_endpoint = db.Column(db.String(256), comment='操作路由')
    old_value = db.Column(db.String(256), comment='旧值')
    new_value = db.Column(db.String(256), comment='新值')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class TSystemOperationLog(Model):
    """操作日志记录表
    """
    __tablename__ = 'SYSTEM_OPERATION_LOG'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='乐观锁')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    REMARK = db.Column(db.String(128), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, comment='更新时间')
