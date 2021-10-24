#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from sqlalchemy import UniqueConstraint

from app.database import DBModel
from app.database import db
from app.utils.log_util import get_logger
from app.utils.time_util import datetime_now_by_utc8


log = get_logger(__name__)


class TWorkspaceCollectionRel(DBModel):
    """空间集合关联表"""
    __tablename__ = 'WORKSPACE_COLLECTION_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='测试集合编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


class TTestElement(DBModel):
    """测试元素表"""
    __tablename__ = 'TEST_ELEMENT'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='版本号')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ELEMENT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='元素编号')
    ELEMENT_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    ELEMENT_REMARK = db.Column(db.String(512), comment='元素描述')
    ELEMENT_TYPE = db.Column(db.String(64), nullable=False, comment='元素类型')
    ELEMENT_CLASS = db.Column(db.String(64), nullable=False, comment='元素实现类')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    META_DATA = db.Column(db.String(512), comment='元数据')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


class TElementProperty(DBModel):
    """测试元素属性表"""
    __tablename__ = 'ELEMENT_PROPERTY'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='版本号')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ELEMENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='元素编号')
    PROPERTY_NAME = db.Column(db.String(256), nullable=False, comment='属性名称')
    PROPERTY_VALUE = db.Column(db.Text, comment='属性值')
    PROPERTY_TYPE = db.Column(db.String(32), nullable=False, default='STR', comment='属性类型')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')
    UniqueConstraint('ELEMENT_NO', 'PROPERTY_NAME', 'DEL_STATE', name='unique_element_property')


class TElementChildRel(DBModel):
    """元素子代关联表"""
    __tablename__ = 'ELEMENT_CHILD_REL'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='版本号')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ROOT_NO = db.Column(db.String(32), index=True, nullable=False, comment='根元素编号')
    PARENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='父元素编号')
    CHILD_NO = db.Column(db.String(32), index=True, nullable=False, comment='子元素编号')
    SERIAL_NO = db.Column(db.Integer, nullable=False, comment='子元素序号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


class TElementBuiltinChildRel(DBModel):
    """内置元素关联表"""
    __tablename__ = 'ELEMENT_BUILTIN_CHILD_REL'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='版本号')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ROOT_NO = db.Column(db.String(32), index=True, nullable=False, comment='根元素编号')
    PARENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='父元素编号')
    CHILD_NO = db.Column(db.String(32), index=True, nullable=False, comment='子元素编号')
    CHILD_TYPE = db.Column(db.String(64), nullable=False, comment='子元素类型')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


# TODO: rename TVariableDataset
# TODO: rename DATADATASET_NO
class TVariableDataset(DBModel):
    """变量集表"""
    __tablename__ = 'VARIABLE_SET'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), comment='空间编号')
    DATASET_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='变量集编号')
    DATASET_NAME = db.Column(db.String(128), nullable=False, comment='变量集名称')
    DATASET_TYPE = db.Column(db.String(128), nullable=False, comment='变量集类型: GLOBAL(全局), ENVIRONMENT(环境), CUSTOM(自定义)')
    DATASET_DESC = db.Column(db.String(256), comment='变量集描述')
    WEIGHT = db.Column(db.Integer, nullable=False, comment='权重')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')
    UniqueConstraint('WORKSPACE_NO', 'DATASET_NAME', 'DATASET_TYPE', 'DEL_STATE', name='unique_workspace_name_type')


class TVariable(DBModel):
    """变量表"""
    __tablename__ = 'VARIABLE'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    DATASET_NO = db.Column(db.String(32), index=True, nullable=False, comment='变量集编号')
    VAR_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='变量编号')
    VAR_NAME = db.Column(db.Text, nullable=False, comment='变量名称')
    VAR_DESC = db.Column(db.String(256), comment='变量描述')
    INITIAL_VALUE = db.Column(db.String(2048), comment='变量值')
    CURRENT_VALUE = db.Column(db.String(2048), comment='当前值')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')
    UniqueConstraint('DATASET_NO', 'VAR_NAME', 'DEL_STATE', name='unique_set_name')


class THttpSamplerHeadersRel(DBModel):
    """元素请求头模板关联表"""
    __tablename__ = 'HTTP_SAMPLER_TEMPLATE_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    SAMPLER_NO = db.Column(db.String(32), index=True, nullable=False, comment='元素编号')
    TEMPLATE_NO = db.Column(db.String(32), index=True, nullable=False, comment='模板编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')
    UniqueConstraint('SAMPLER_NO', 'TEMPLATE_NO', 'DEL_STATE', name='unique_sampler_template')


class THttpHeadersTemplate(DBModel):
    """请求头模板表"""
    __tablename__ = 'HTTP_HEADERS_TEMPLATE'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), comment='空间编号')
    TEMPLATE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='模板编号')
    TEMPLATE_NAME = db.Column(db.String(128), nullable=False, comment='模板名称')
    TEMPLATE_DESC = db.Column(db.String(256), comment='模板描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')
    UniqueConstraint('TEMPLATE_NAME', 'DEL_STATE', name='unique_templatename')


class THttpHeader(DBModel):
    """HTTP头部表"""
    __tablename__ = 'HTTP_HEADER'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    TEMPLATE_NO = db.Column(db.String(32), index=True, nullable=False, comment='模板编号')
    HEADER_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='请求头编号')
    HEADER_NAME = db.Column(db.String(256), nullable=False, comment='请求头名称')
    HEADER_VALUE = db.Column(db.Text, nullable=False, comment='请求头值')
    HEADER_DESC = db.Column(db.String(256), comment='请求头描述')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')
    UniqueConstraint('TEMPLATE_NO', 'HEADER_NAME', 'DEL_STATE', name='unique_template_header')


# TODO: rename TDataBaseConfiguration
class TDataBaseConfiguration(DBModel):
    """SQL配置表"""
    __tablename__ = 'SQL_CONFIGURATION'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    DB_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='配置编号')  # TODO: rename DB_NO
    DB_NAME = db.Column(db.String(256), nullable=False, comment='配置名称')  # TODO: rename DB_NAME
    DB_DESC = db.Column(db.String(256), nullable=False, comment='配置描述')  # TODO: rename DB_DESC
    DB_TYPE = db.Column(db.String(64), nullable=False, comment='数据库类型')
    DB_URL = db.Column(db.String(256), nullable=False, comment='数据库地址')
    USER_NAME = db.Column(db.String(256), nullable=False, comment='数据库用户名称')
    PASSWORD = db.Column(db.String(256), nullable=False, comment='数据库密码')
    CONNECTION_NAME = db.Column(db.String(256), nullable=False, comment='数据库连接变量')  # TODO: rename CONNECTION_NAME
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


class TElementTagRel(DBModel):
    """元素标签关联表"""
    __tablename__ = 'ELEMENT_TAG_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ELEMENT_NO = db.Column(db.String(32), comment='元素编号')
    TAG_NO = db.Column(db.String(32), index=True, nullable=False, comment='标签编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')
    UniqueConstraint('ELEMENT_NO', 'TAG_NO', 'DEL_STATE', name='unique_element_tag')


# TODO: rename TTestplan
class TTestplan(DBModel):
    """测试计划表"""
    __tablename__ = 'TESTPLAN'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), nullable=False, comment='空间编号')
    PLAN_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='计划编号')
    PLAN_NAME = db.Column(db.String(256), nullable=False, comment='计划名称')
    PLAN_DESC = db.Column(db.String(512), comment='计划描述')
    VERSION_NUMBER = db.Column(db.String(128), comment='需求版本号')  # TODO: rename VERSION_NUMBER
    ENVIRONMENT = db.Column(db.String(128), comment='测试环境')
    # TOTAL = db.Column(db.Integer, nullable=False, default=0, comment='脚本总数')  # TODO: del 查询时计算
    # RUNNING_STATE = db.Column(db.String(64), comment='运行状态，待运行/运行中/已完成')  # TODO: del
    TEST_PHASE = db.Column(db.String(64), comment='测试阶段，待测试/冒烟测试/系统测试/回归测试/已完成')
    STATE = db.Column(db.String(64), comment='计划状态，待开始/进行中/已完成')
    START_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='开始时间')
    END_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='结束时间')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


# TODO: rename TTestplanSettings
class TTestplanSettings(DBModel):
    """测试计划设置表"""
    __tablename__ = 'TESTPLAN_SETTINGS'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    PLAN_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='计划编号')
    CONCURRENCY = db.Column(db.Integer, nullable=False, default=1, comment='并发数')
    ITERATIONS = db.Column(db.Integer, nullable=False, default=0, comment='计划迭代次数')
    DELAY = db.Column(db.Integer, nullable=False, default=0, comment='运行脚本的间隔时间，单位ms')
    SAVE = db.Column(db.Boolean, nullable=False, default=True, comment='是否保存数据至报告中')
    SAVE_ON_ERROR = db.Column(db.Boolean, nullable=False, default=True, comment='是否只保存失败的数据至报告中')
    STOP_TEST_ON_ERROR_COUNT = db.Column(db.Integer, default=0, comment='错误指定的错误后停止测试计划')
    USE_CURRENT_VALUE = db.Column(db.Boolean, nullable=False, default=False, comment='是否使用变量的当前值')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


# TODO: rename TTestplanDatasetRel
class TTestplanDatasetRel(DBModel):
    """测试计划数据集关联表"""
    __tablename__ = 'TESTPLAN_DATASET_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    PLAN_NO = db.Column(db.String(32), index=True, nullable=False, comment='计划编号')
    DATASET_NO = db.Column(db.String(32), index=True, nullable=False, comment='变量集编号')  # TODO: rename DATASET_NO
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')
    UniqueConstraint('PLAN_NO', 'DATASET_NO', 'DEL_STATE', name='unique_plan_set')


# TODO: rename TTestplanItems
class TTestplanItems(DBModel):
    """测试计划项目明细表"""
    __tablename__ = 'TESTPLAN_ITEMS'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    PLAN_NO = db.Column(db.String(32), index=True, nullable=False, comment='计划编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='集合编号')
    SERIAL_NO = db.Column(db.Integer, nullable=False, comment='序号')
    # RUNNING_STATE = db.Column(db.String(64), comment='运行状态，待运行/运行中/已完成')  # TODO: del
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')
    UniqueConstraint('PLAN_NO', 'COLLECTION_NO', 'DEL_STATE', name='unique_plan_collection')


class TTestplanExecution(DBModel):
    """测试计划执行记录表"""
    __tablename__ = 'TESTPLAN_EXECUTION'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    PLAN_NO = db.Column(db.String(32), index=True, nullable=False, comment='计划编号')
    EXECUTION_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='执行编号')
    RUNNING_STATE = db.Column(db.String(64), comment='运行状态，待运行/运行中/已完成')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


class TTestplanExecutionSettings(DBModel):
    """测试计划执行设置表"""
    __tablename__ = 'TESTPLAN_EXECUTION_SETTINGS'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    EXECUTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='执行编号')
    ...
    CONCURRENCY = db.Column(db.Integer, nullable=False, default=1, comment='并发数')
    ITERATIONS = db.Column(db.Integer, nullable=False, default=0, comment='计划迭代次数')
    DELAY = db.Column(db.Integer, nullable=False, default=0, comment='运行脚本的间隔时间，单位ms')
    SAVE = db.Column(db.Boolean, nullable=False, default=True, comment='是否保存数据至报告中')
    SAVE_ON_ERROR = db.Column(db.Boolean, nullable=False, default=True, comment='是否只保存失败的数据至报告中')
    STOP_TEST_ON_ERROR_COUNT = db.Column(db.Integer, default=0, comment='错误指定的错误后停止测试计划')
    USE_CURRENT_VALUE = db.Column(db.Boolean, nullable=False, default=False, comment='是否使用变量的当前值')
    ...
    DATASETS = db.Column(db.Text, comment='关联的数据集字典')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


class TTestplanExecutionItems(DBModel):
    """测试计划执行项目明细表"""
    __tablename__ = 'TESTPLAN_EXECUTION_ITEMS'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    EXECUTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='执行编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='集合编号')
    SERIAL_NO = db.Column(db.Integer, nullable=False, comment='序号')
    RUNNING_STATE = db.Column(db.String(64), comment='运行状态，待运行/运行中/已完成')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


class TTestReport(DBModel):
    """测试报告表"""
    __tablename__ = 'TEST_REPORT'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), nullable=False, comment='空间编号')
    PLAN_NO = db.Column(db.String(32), nullable=False, comment='计划编号')
    EXECUTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='执行编号')
    REPORT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='报告编号')
    REPORT_NAME = db.Column(db.String(256), nullable=False, comment='报告名称')
    REPORT_DESC = db.Column(db.String(512), comment='报告描述')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer, comment='耗时')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')
    UniqueConstraint('WORKSPACE_NO', 'PLAN_NO', 'REPORT_NO', 'DEL_STATE', name='unique_workspace_plan_report')


class TTestCollectionResult(DBModel):
    """测试集合结果表"""
    __tablename__ = 'TEST_COLLECTION_RESULT'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    REPORT_NO = db.Column(db.String(32), index=True, nullable=False, comment='报告编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='集合编号')
    COLLECTION_ID = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='运行时集合的对象id')
    COLLECTION_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    COLLECTION_REMARK = db.Column(db.String(512), comment='元素描述')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer, comment='耗时')
    SUCCESS = db.Column(db.Boolean, comment='是否成功')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


class TTestGroupResult(DBModel):
    """测试分组结果表"""
    __tablename__ = 'TEST_GROUP_RESULT'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    REPORT_NO = db.Column(db.String(32), index=True, nullable=False, comment='报告编号')
    COLLECTION_ID = db.Column(db.String(32), index=True, nullable=False, comment='运行时集合的对象id')
    GROUP_ID = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='运行时分组的对象id')
    GROUP_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    GROUP_REMARK = db.Column(db.String(512), comment='元素描述')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer, comment='耗时')
    SUCCESS = db.Column(db.Boolean, comment='是否成功')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')


class TTestSamplerResult(DBModel):
    """测试取样器结果表"""
    __tablename__ = 'TEST_SAMPLER_RESULT'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    REPORT_NO = db.Column(db.String(32), index=True, nullable=False, comment='报告编号')
    COLLECTION_ID = db.Column(db.String(32), index=True, nullable=False, comment='运行时集合的对象id')
    GROUP_ID = db.Column(db.String(32), index=True, nullable=False, comment='运行时分组的对象id')
    PARENT_ID = db.Column(db.String(32), index=True, comment='运行时子代取样器的父级的对象id')
    SAMPLER_ID = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='运行时取样器的对象id')
    SAMPLER_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    SAMPLER_REMARK = db.Column(db.String(512), comment='元素描述')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer, comment='耗时')
    SUCCESS = db.Column(db.Boolean, comment='是否成功')
    REQUEST_URL = db.Column(db.Text, comment='请求地址')
    REQUEST_HEADERS = db.Column(db.Text, comment='请求头')
    REQUEST_DATA = db.Column(db.Text, comment='请求数据')
    RESPONSE_CODE = db.Column(db.Text, comment='响应码')
    RESPONSE_HEADERS = db.Column(db.Text, comment='响应头')
    RESPONSE_DATA = db.Column(db.Text, comment='响应数据')
    ERROR_ASSERTION = db.Column(db.Text, comment='失败断言数据')  # TODO: rename FAILED_ASSERTION
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime_now_by_utc8, onupdate=datetime_now_by_utc8, comment='更新时间')
