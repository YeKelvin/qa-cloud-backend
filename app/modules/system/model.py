#!/usr/bin/ python3
# @File    : model.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from app.database import BaseColumn
from app.database import DBModel
from app.database import db


class TRestApiLog(DBModel, BaseColumn):
    """RestAPI日志表"""
    __tablename__ = 'REST_API_LOG'
    LOG_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='日志编号')
    DESC = db.Column(db.String(256), comment='请求描述')
    IP = db.Column(db.String(32), comment='请求IP')
    URI = db.Column(db.String(256), comment='请求路径')
    METHOD = db.Column(db.String(128), comment='请求方法')
    REQUEST = db.Column(db.Text, comment='请求数据')
    RESPONSE = db.Column(db.Text, comment='响应数据')
    SUCCESS = db.Column(db.Boolean, comment='是否成功')
    ELAPSED_TIME = db.Column(db.Integer, comment='服务耗时')


class TSystemOperationLogContent(DBModel, BaseColumn):
    # TODO: SYSTEM_DATA_CHANGE_LOG
    """数据变更日志表"""
    __tablename__ = 'SYSTEM_OPERATION_LOG_CONTENT'
    LOG_NO = db.Column(db.String(64), index=True, nullable=False, comment='日志编号')
    OPERATION_TYPE = db.Column(db.String(32), nullable=False, comment='操作类型(INSERT:新增, UPDATE:修改, DELETE:删除)')
    TABLE_NAME = db.Column(db.String(128), comment='表名')
    ROW_ID = db.Column(db.Integer, comment='数据ID')
    COLUMN_NAME = db.Column(db.String(128), comment='列名')
    OLD_VALUE = db.Column(db.Text, comment='旧值')
    NEW_VALUE = db.Column(db.Text, comment='新值')
