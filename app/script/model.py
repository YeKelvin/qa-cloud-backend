#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from datetime import datetime

from sqlalchemy import UniqueConstraint

from app.database import DBModel
from app.database import db
from app.utils.log_util import get_logger


log = get_logger(__name__)


class TWorkspaceCollectionRel(DBModel):
    """工作空间集合关联表"""
    __tablename__ = 'WORKSPACE_COLLECTION_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='工作空间编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='测试集合编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTestElement(DBModel):
    """测试元素表"""
    __tablename__ = 'TEST_ELEMENT'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ELEMENT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='元素编号')
    ELEMENT_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    ELEMENT_REMARK = db.Column(db.String(512), comment='元素描述')
    ELEMENT_TYPE = db.Column(db.String(64), nullable=False, comment='元素类型')
    ELEMENT_CLASS = db.Column(db.String(64), nullable=False, comment='元素类')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TElementProperty(DBModel):
    """测试元素属性表"""
    __tablename__ = 'ELEMENT_PROPERTY'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ELEMENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='元素编号')
    PROPERTY_NAME = db.Column(db.String(256), nullable=False, comment='属性名称')
    PROPERTY_VALUE = db.Column(db.String(4096), comment='属性值')
    PROPERTY_TYPE = db.Column(db.String(32), nullable=False, default='STR', comment='属性类型')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    UniqueConstraint('ELEMENT_NO', 'PROPERTY_NAME', name='idx_elementno_propertyno')


class TElementChildRel(DBModel):
    """元素子代关联表"""
    __tablename__ = 'ELEMENT_CHILD_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ROOT_NO = db.Column(db.String(32), comment='根元素编号')
    PARENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='父元素编号')
    CHILD_NO = db.Column(db.String(32), index=True, nullable=False, comment='子元素编号')
    CHILD_ORDER = db.Column(db.Integer, nullable=False, comment='子元素序号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TVariableSet(DBModel):
    """变量集表"""
    __tablename__ = 'VARIABLE_SET'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), comment='工作空间编号')
    SET_NO = db.Column(db.String(32), index=True, nullable=False, comment='变量集编号')
    SET_NAME = db.Column(db.String(128), nullable=False, comment='变量集名称')
    SET_TYPE = db.Column(db.String(128), nullable=False, comment='变量集类型: GLOBAL(全局), ENVIRONMENT(环境), CUSTOM(自定义)')
    SET_DESC = db.Column(db.String(256), comment='变量集描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TVariable(DBModel):
    """变量表"""
    __tablename__ = 'VARIABLE'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    SET_NO = db.Column(db.String(32), index=True, nullable=False, comment='变量集编号')
    VAR_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='变量编号')
    VAR_NAME = db.Column(db.String(256), nullable=False, comment='变量名称')
    VAR_DESC = db.Column(db.String(256), comment='变量描述')
    INITIAL_VALUE = db.Column(db.String(512), nullable=False, comment='变量值')
    CURRENT_VALUE = db.Column(db.String(512), nullable=False, comment='当前值')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class THTTPHeaderSet:
    """HTTP头部集合表"""
    __tablename__ = 'HTTP_HEADER_SET'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    SET_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='头部集编号')
    SET_NAME = db.Column(db.String(128), nullable=False, comment='头部集名称')
    SET_DESC = db.Column(db.String(256), comment='头部集描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class THTTPHeader(DBModel):
    """HTTP头部表"""
    __tablename__ = 'HTTP_HEADER'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    HEADER_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='头部编号')
    HEADER_KEY = db.Column(db.String(256), nullable=False, comment='头部名称')
    HEADER_VALUE = db.Column(db.String(1024), nullable=False, comment='头部值')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TSQLConfiguration(DBModel):
    """SQL配置表"""
    __tablename__ = 'SQL_CONFIGURATION'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    CONFIG_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='配置编号')
    CONFIG_NAME = db.Column(db.String(256), nullable=False, comment='配置名称')
    CONFIG_DESC = db.Column(db.String(256), nullable=False, comment='配置描述')
    CONNECTION_VARIABLE_NAME = db.Column(db.String(256), nullable=False, comment='数据库连接变量')
    DB_TYPE = db.Column(db.String(64), nullable=False, comment='数据库类型')
    DB_URL = db.Column(db.String(256), nullable=False, comment='数据库地址')
    USER_NAME = db.Column(db.String(256), nullable=False, comment='数据库用户名称')
    PASSWORD = db.Column(db.String(256), nullable=False, comment='数据库密码')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
