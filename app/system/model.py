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
    """操作日志记录表"""
    __tablename__ = 'SYSTEM_OPERATION_LOG'
    LOG_NO = db.Column(db.String(32), index=True, nullable=False, comment='日志编号')
    USER_NO = db.Column(db.String(32), comment='用户编号')
    LOGIN_NAME = db.Column(db.String(64), comment='登录账号')
    CONTENT = db.Column(db.String(512), comment='操作内容')
    OPT_TYPE = db.Column(db.String(32), comment='操作类型(LOGIN:登录, INSERT:新增, DELETE:删除, UPDATE:修改, QUERY:查询)')
    IP = db.Column(db.String(64), comment='IP地址')
    INPUT_PARAMS = db.Column(db.String(4096), comment='输入参数')
    OUTPUT_PARAMS = db.Column(db.String(4096), comment='输出参数')
    EXCEPTION_MSG = db.Column(db.String(4096), comment='异常信息')
    REQ_TIME = db.Column(db.DateTime, comment='请求时间')
    RES_TIME = db.Column(db.DateTime, comment='响应时间')
    TIME_CONSUMING = db.Column(db.Integer, comment='耗时(ms)')
