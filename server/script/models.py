#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from datetime import datetime

from server.database import DBModel, db
from server.common.utils.log_util import get_logger

log = get_logger(__name__)


class TWorkspace(DBModel):
    """工作空间表
    """
    __tablename__ = 'WORKSPACE'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='工作空间编号')
    WORKSPACE_NAME = db.Column(db.String(128), nullable=False, comment='工作空间名称')
    WORKSPACE_TYPE = db.Column(db.String(128), nullable=False, comment='工作空间类型')
    WORKSPACE_DESC = db.Column(db.String(256), comment='工作空间描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TWorkspaceTopicRel(DBModel):
    """项目主题关联表
    """
    __tablename__ = 'WORKSPACE_TOPIC_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), nullable=False, comment='工作空间编号')
    TOPIC_NO = db.Column(db.String(32), nullable=False, comment='主题编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TWorkspaceCollectionRel(DBModel):
    """项目集合关联表
    """
    __tablename__ = 'WORKSPACE_COLLECTION_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), nullable=False, comment='工作空间编号')
    COLLECTION_NO = db.Column(db.String(32), nullable=False, comment='测试集合编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TWorkspaceUserRel(DBModel):
    """项目用户关联表
    """
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


class TTestTopic(DBModel):
    """测试主题表
    """
    __tablename__ = 'TEST_TOPIC'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    TOPIC_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='主题编号')
    TOPIC_NAME = db.Column(db.String(128), nullable=False, comment='主题名称')
    TOPIC_DESC = db.Column(db.String(256), comment='主题描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTopicCollectionRel(DBModel):
    """主题集合关联表
    """
    __tablename__ = 'TOPIC_COLLECTION_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    TOPIC_NO = db.Column(db.String(32), nullable=False, comment='主题编号')
    COLLECTION_NO = db.Column(db.String(32), nullable=False, comment='测试集合编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTestElement(DBModel):
    """测试元素表
    """
    __tablename__ = 'TEST_ELEMENT'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ELEMENT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='元素编号')
    ELEMENT_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    ELEMENT_COMMENTS = db.Column(db.String(512), comment='元素描述')
    ELEMENT_TYPE = db.Column(db.String(64), nullable=False, comment='元素类型')
    ENABLED = db.Column(db.Boolean, nullable=False, comment='是否启用')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TElementProperty(DBModel):
    """测试元素属性表
    """
    __tablename__ = 'ELEMENT_PROPERTY'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ELEMENT_NO = db.Column(db.String(32), nullable=False, comment='元素编号')
    PROPERTY_NAME = db.Column(db.String(256), nullable=False, comment='属性名称')
    PROPERTY_VALUE = db.Column(db.String(4096), nullable=False, comment='属性值')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TElementChildRel(DBModel):
    """元素子代关联表
    """
    __tablename__ = 'ELEMENT_CHILD_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    # todo 元素关联表增加集合编号，方便查找子元素所属的集合编号
    COLLECTION_NO = db.Column(db.String(32), nullable=False, comment='测试集合编号')
    PARENT_NO = db.Column(db.String(32), nullable=False, comment='父元素编号')
    CHILD_NO = db.Column(db.String(32), index=True, nullable=False, comment='子元素编号')
    CHILD_ORDER = db.Column(db.Integer, nullable=False, comment='子元素序号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TEnvironmentVariableCollection(DBModel):
    """环境变量集合表
    """
    __tablename__ = 'ENVIRONMENT_VARIABLE_COLLECTION'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    COLLECTION_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='环境集合编号')
    COLLECTION_NAME = db.Column(db.String(128), nullable=False, comment='环境集合名称')
    COLLECTION_DESC = db.Column(db.String(256), comment='环境集合描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TEnvironmentVariableCollectionRel(DBModel):
    """环境变量集合关联表
    """
    __tablename__ = 'ENVIRONMENT_VARIABLE_COLLECTION_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    COLLECTION_NO = db.Column(db.String(32), nullable=False, comment='环境集合编号')
    ENV_NO = db.Column(db.String(32), nullable=False, comment='环境变量编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TEnvironmentVariable(DBModel):
    """环境变量表
    """
    __tablename__ = 'ENVIRONMENT_VARIABLE'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ENV_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='环境变量编号')
    ENV_KEY = db.Column(db.String(256), nullable=False, comment='环境变量名称')
    ENV_VALUE = db.Column(db.String(512), nullable=False, comment='环境变量值')
    ENV_DESC = db.Column(db.String(256), comment='环境变量描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class THTTPHeaderCollection:
    """HTTP头部集合表
    """
    __tablename__ = 'HTTP_HEADER_COLLECTION'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    COLLECTION_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='头部集合编号')
    COLLECTION_NAME = db.Column(db.String(128), nullable=False, comment='头部集合名称')
    COLLECTION_DESC = db.Column(db.String(256), comment='头部集合描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class THTTPHeaderCollectionRel:
    """HTTP头部集合关联表
    """
    __tablename__ = 'HTTP_HEADER_COLLECTION_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    COLLECTION_NO = db.Column(db.String(32), nullable=False, comment='头部集合编号')
    HEADER_NO = db.Column(db.String(32), nullable=False, comment='头部编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class THTTPHeader(DBModel):
    """HTTP头部表
    """
    __tablename__ = 'HTTP_HEADER'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    HEADER_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='头部编号')
    HEADER_KEY = db.Column(db.String(256), nullable=False, comment='头部名称')
    HEADER_VALUE = db.Column(db.String(1024), nullable=False, comment='头部值')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TSQLConfiguration(DBModel):
    """SQL配置表
    """
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


class TElementPackage(DBModel):
    """元素封装表
    """
    __tablename__ = 'ELEMENT_PACKAGE'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    PACKAGE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='封装编号')
    PACKAGE_DESC = db.Column(db.String(256), nullable=False, comment='封装描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TPackageElementRel(DBModel):
    """封装元素关联表
    """
    __tablename__ = 'PACKAGE_ELEMENT_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    PACKAGE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='封装编号')
    ELEMENT_NO = db.Column(db.String(256), nullable=False, comment='元素编号')
    ELEMENT_ORDER = db.Column(db.Integer, nullable=False, comment='元素序号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TScriptActivityLog(DBModel):
    """脚本活动日志表
    """
    __tablename__ = 'SCRIPT_ACTIVITY_LOG'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), nullable=False, comment='工作空间编号')
    TOPIC_NO = db.Column(db.String(32), nullable=False, comment='主题编号')
    COLLECTION_NO = db.Column(db.String(32), nullable=False, comment='主题编号')
    GROUP_NO = db.Column(db.String(32), nullable=False, comment='案例编号')
    ACTIVITY_TYPE = db.Column(db.String(32), nullable=False, comment='活动类型')
    ACTIVITY_DESC = db.Column(db.String(256), nullable=False, comment='活动描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
