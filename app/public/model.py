#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2021-08-18 15:27:03
# @Author  : Kelvin.Ye
from datetime import datetime

from app.database import DBModel
from app.database import db
from app.utils.log_util import get_logger


log = get_logger(__name__)


class TWorkspace(DBModel):
    """工作空间表"""
    __tablename__ = 'WORKSPACE'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='工作空间编号')
    WORKSPACE_NAME = db.Column(db.String(128), nullable=False, comment='工作空间名称')
    WORKSPACE_TYPE = db.Column(db.String(128), nullable=False, comment='工作空间类型')
    WORKSPACE_SCOPE = db.Column(db.String(128), nullable=False, comment='工作空间作用域')
    WORKSPACE_DESC = db.Column(db.String(256), comment='工作空间描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TWorkspaceUserRel(DBModel):
    """工作空间用户关联表"""
    __tablename__ = 'WORKSPACE_USER_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), nullable=False, comment='工作空间编号')
    USER_NO = db.Column(db.String(32), nullable=False, comment='用户编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTag(DBModel):
    """标签表"""
    __tablename__ = 'TAG'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    TAG_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='标签编号')
    TAG_NAME = db.Column(db.String(256), nullable=False, comment='标签名称')
    TAG_DESC = db.Column(db.String(256), nullable=False, comment='标签描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
