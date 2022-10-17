#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from app.database import BaseColumn
from app.database import DBModel
from app.database import db


class TWorkspaceCollection(DBModel, BaseColumn):
    """空间集合表"""
    __tablename__ = 'WORKSPACE_COLLECTION'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='测试集合编号')


class TWorkspaceComponent(DBModel, BaseColumn):
    """空间组件表"""
    __tablename__ = 'WORKSPACE_COMPONENT'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    COMPONENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='组件编号')
    COMPONENT_TYPE = db.Column(db.String(64), nullable=False, comment='组件类型')
    SORT_NUMBER = db.Column(db.Integer, nullable=False, comment='排序号')
    SORT_WEIGHT = db.Column(db.Integer, nullable=False, comment='排序权重')


class TTestElement(DBModel, BaseColumn):
    """测试元素表"""
    __tablename__ = 'TEST_ELEMENT'
    ELEMENT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='元素编号')
    ELEMENT_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    ELEMENT_REMARK = db.Column(db.String(512), comment='元素描述')
    ELEMENT_TYPE = db.Column(db.String(64), nullable=False, comment='元素类型')
    ELEMENT_CLASS = db.Column(db.String(64), nullable=False, comment='元素实现类')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    META_DATA = db.Column(db.String(512), comment='元数据')


class TElementProperty(DBModel, BaseColumn):
    """元素属性表"""
    __tablename__ = 'ELEMENT_PROPERTY'
    # TODO: ROOT_NO = db.Column(db.String(32), index=True, nullable=False, comment='根元素编号')
    # TODO: PARENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='父元素编号')
    ELEMENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='元素编号')
    PROPERTY_NAME = db.Column(db.String(256), nullable=False, comment='属性名称')
    PROPERTY_VALUE = db.Column(db.Text, comment='属性值')
    PROPERTY_TYPE = db.Column(db.String(32), nullable=False, default='STR', comment='属性类型')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    UniqueConstraint('ELEMENT_NO', 'PROPERTY_NAME', 'DELETED', name='unique_element_property')


class TElementOptions(DBModel, BaseColumn):
    """元素选项表"""
    __tablename__ = 'ELEMENT_OPTIONS'
    ELEMENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='元素编号')
    OPTION_NAME = db.Column(db.String(256), nullable=False, comment='选项名称')
    OPTION_VALUE = db.Column(db.Text, comment='选项值')
    OPTION_TYPE = db.Column(db.String(32), nullable=False, default='STR', comment='选项类型')


class TElementChildren(DBModel, BaseColumn):
    """元素子代表"""
    __tablename__ = 'ELEMENT_CHILDREN'
    ROOT_NO = db.Column(db.String(32), index=True, nullable=False, comment='根元素编号')
    PARENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='父元素编号')
    CHILD_NO = db.Column(db.String(32), index=True, nullable=False, comment='子元素编号')
    SORT_NO = db.Column(db.Integer, nullable=False, comment='子元素序号')


class TElementBuiltinChildren(DBModel, BaseColumn):
    """内置元素表"""
    __tablename__ = 'ELEMENT_BUILTIN_CHILDREN'
    ROOT_NO = db.Column(db.String(32), index=True, nullable=False, comment='根元素编号')
    PARENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='父元素编号')
    CHILD_NO = db.Column(db.String(32), index=True, nullable=False, comment='子元素编号')
    CHILD_TYPE = db.Column(db.String(64), nullable=False, comment='子元素类型')
    SORT_NUMBER = db.Column(db.Integer, nullable=False, comment='排序号')
    SORT_WEIGHT = db.Column(db.Integer, nullable=False, comment='排序权重')


class TVariableDataset(DBModel, BaseColumn):
    """变量集表"""
    __tablename__ = 'VARIABLE_DATASET'
    WORKSPACE_NO = db.Column(db.String(32), index=True, comment='空间编号')
    DATASET_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='变量集编号')
    DATASET_NAME = db.Column(db.String(128), nullable=False, comment='变量集名称')
    DATASET_TYPE = db.Column(db.String(128), nullable=False, comment='变量集类型: GLOBAL(全局), ENVIRONMENT(环境), CUSTOM(自定义)')
    DATASET_DESC = db.Column(db.String(256), comment='变量集描述')
    WEIGHT = db.Column(db.Integer, nullable=False, comment='权重')
    UniqueConstraint('WORKSPACE_NO', 'DATASET_NAME', 'DATASET_TYPE', 'DELETED', name='unique_workspace_dataset')


class TVariable(DBModel, BaseColumn):
    """变量表"""
    __tablename__ = 'VARIABLE'
    DATASET_NO = db.Column(db.String(32), index=True, nullable=False, comment='变量集编号')
    VAR_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='变量编号')
    VAR_NAME = db.Column(db.Text, nullable=False, comment='变量名称')
    VAR_DESC = db.Column(db.String(256), comment='变量描述')
    INITIAL_VALUE = db.Column(db.String(2048), comment='变量值')
    CURRENT_VALUE = db.Column(db.String(2048), comment='当前值')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    UniqueConstraint('DATASET_NO', 'VAR_NAME', 'DELETED', name='unique_dataset_variable')


class THttpHeaderTemplateRef(DBModel, BaseColumn):
    """HTTP请求头模板表"""
    __tablename__ = 'HTTP_HEADER_TEMPLATE_REF'
    SAMPLER_NO = db.Column(db.String(32), index=True, nullable=False, comment='元素编号')
    TEMPLATE_NO = db.Column(db.String(32), index=True, nullable=False, comment='模板编号')
    UniqueConstraint('SAMPLER_NO', 'TEMPLATE_NO', 'DELETED', name='unique_sampler_template')


class THttpHeaderTemplate(DBModel, BaseColumn):
    """请求头模板表"""
    __tablename__ = 'HTTP_HEADER_TEMPLATE'
    WORKSPACE_NO = db.Column(db.String(32), index=True, comment='空间编号')
    TEMPLATE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='模板编号')
    TEMPLATE_NAME = db.Column(db.String(128), nullable=False, comment='模板名称')
    TEMPLATE_DESC = db.Column(db.String(256), comment='模板描述')
    UniqueConstraint('WORKSPACE_NO', 'TEMPLATE_NAME', 'DELETED', name='unique_workspace_template')


class THttpHeader(DBModel, BaseColumn):
    """HTTP头部表"""
    __tablename__ = 'HTTP_HEADER'
    TEMPLATE_NO = db.Column(db.String(32), index=True, nullable=False, comment='模板编号')
    HEADER_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='请求头编号')
    HEADER_NAME = db.Column(db.String(256), nullable=False, comment='请求头名称')
    HEADER_VALUE = db.Column(db.Text, nullable=False, comment='请求头值')
    HEADER_DESC = db.Column(db.String(256), comment='请求头描述')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    UniqueConstraint('TEMPLATE_NO', 'HEADER_NAME', 'DELETED', name='unique_template_header')


class TDatabaseConfig(DBModel, BaseColumn):
    """SQL配置表"""
    __tablename__ = 'DATABASE_CONFIG'
    WORKSPACE_NO = db.Column(db.String(32), index=True, comment='空间编号')
    CONFIG_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='配置编号')
    CONFIG_NAME = db.Column(db.String(256), nullable=False, comment='配置名称')
    CONFIG_DESC = db.Column(db.String(256), comment='配置描述')
    VARIABLE_NAME = db.Column(db.String(256), nullable=False, comment='变量名称')
    DATABASE_TYPE = db.Column(db.String(64), nullable=False, comment='数据库类型')
    USERNAME = db.Column(db.String(256), nullable=False, comment='数据库用户名称')
    PASSWORD = db.Column(db.String(256), nullable=False, comment='数据库用户密码')
    HOST = db.Column(db.String(128), nullable=False, comment='数据库主机')
    PORT = db.Column(db.String(32), nullable=False, comment='数据库端口')
    QUERY = db.Column(db.String(256), comment='数据库主机地址')
    DATABASE = db.Column(db.String(256), nullable=False, comment='数据库名称')
    CONNECT_TIMEOUT = db.Column(db.String(128), nullable=False, comment='连接超时时间')
    UniqueConstraint('WORKSPACE_NO', 'CONFIG_NAME', 'DATABASE_TYPE', 'DELETED', name='unique_workspace_db')


class TElementTag(DBModel, BaseColumn):
    """元素标签表"""
    __tablename__ = 'ELEMENT_TAG'
    ELEMENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='元素编号')
    TAG_NO = db.Column(db.String(32), index=True, nullable=False, comment='标签编号')
    UniqueConstraint('ELEMENT_NO', 'TAG_NO', 'DELETED', name='unique_element_tag')


class TTestplan(DBModel, BaseColumn):
    """测试计划表"""
    __tablename__ = 'TESTPLAN'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    PLAN_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='计划编号')
    PLAN_NAME = db.Column(db.String(256), nullable=False, comment='计划名称')
    PLAN_DESC = db.Column(db.String(512), comment='计划描述')
    PRODUCT_REQUIREMENTS_VERSION = db.Column(db.String(128), comment='需求版本号')
    COLLECTION_TOTAL = db.Column(db.Integer, nullable=False, default=0, comment='脚本总数')
    TEST_PHASE = db.Column(db.String(64), comment='测试阶段，待测试/冒烟测试/系统测试/回归测试/已完成')
    STATE = db.Column(db.String(64), comment='计划状态，待开始/进行中/已完成')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')


class TTestplanSettings(DBModel, BaseColumn):
    """测试计划设置表"""
    __tablename__ = 'TESTPLAN_SETTINGS'
    PLAN_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='计划编号')
    CONCURRENCY = db.Column(db.Integer, nullable=False, default=1, comment='并发数')
    ITERATIONS = db.Column(db.Integer, nullable=False, default=0, comment='计划迭代次数')
    DELAY = db.Column(db.Integer, nullable=False, default=0, comment='运行脚本的间隔时间，单位ms')
    SAVE = db.Column(db.Boolean, nullable=False, default=True, comment='是否保存数据至报告中')
    SAVE_ON_ERROR = db.Column(db.Boolean, nullable=False, default=True, comment='是否只保存失败的数据至报告中')
    STOP_TEST_ON_ERROR_COUNT = db.Column(db.Integer, default=0, comment='错误指定的错误后停止测试计划')
    USE_CURRENT_VALUE = db.Column(db.Boolean, nullable=False, default=False, comment='是否使用变量的当前值')
    NOTIFICATION_ROBOT_LIST = db.Column(JSONB, comment='通知机器人列表')


class TTestplanItems(DBModel, BaseColumn):
    """测试计划项目明细表"""
    __tablename__ = 'TESTPLAN_ITEMS'
    PLAN_NO = db.Column(db.String(32), index=True, nullable=False, comment='计划编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='集合编号')
    SORT_NO = db.Column(db.Integer, nullable=False, comment='序号')
    UniqueConstraint('PLAN_NO', 'COLLECTION_NO', 'DELETED', name='unique_plan_collection')


class TTestplanExecution(DBModel, BaseColumn):
    """测试计划执行记录表"""
    __tablename__ = 'TESTPLAN_EXECUTION'
    PLAN_NO = db.Column(db.String(32), index=True, nullable=False, comment='计划编号')
    EXECUTION_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='执行编号')
    RUNNING_STATE = db.Column(db.String(64), comment='运行状态，待运行/运行中/迭代中/已完成/已中断')
    ENVIRONMENT = db.Column(db.String(128), comment='测试环境')
    TEST_PHASE = db.Column(db.String(64), comment='测试阶段')
    ITERATION_COUNT = db.Column(db.Integer, nullable=False, default=0, comment='迭代次数')
    INTERRUPT = db.Column(db.Boolean, nullable=False, default=False, comment='是否中断运行')
    INTERRUPT_BY = db.Column(db.String(64), comment='中断人')
    INTERRUPT_TIME = db.Column(db.DateTime, comment='中断时间')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer, comment='耗时')


class TTestplanExecutionSettings(DBModel, BaseColumn):
    """测试计划执行记录设置表"""
    __tablename__ = 'TESTPLAN_EXECUTION_SETTINGS'
    EXECUTION_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='执行编号')
    CONCURRENCY = db.Column(db.Integer, nullable=False, default=1, comment='并发数')
    ITERATIONS = db.Column(db.Integer, nullable=False, default=0, comment='计划迭代次数')
    DELAY = db.Column(db.Integer, nullable=False, default=0, comment='运行脚本的间隔时间，单位ms')
    SAVE = db.Column(db.Boolean, nullable=False, default=True, comment='是否保存数据至报告中')
    SAVE_ON_ERROR = db.Column(db.Boolean, nullable=False, default=True, comment='是否只保存失败的数据至报告中')
    STOP_TEST_ON_ERROR_COUNT = db.Column(db.Integer, default=0, comment='错误指定的错误后停止测试计划')
    VARIABLE_DATASET_LIST = db.Column(JSONB, comment='变量集列表')
    USE_CURRENT_VALUE = db.Column(db.Boolean, nullable=False, default=False, comment='是否使用变量的当前值')
    NOTIFICATION_ROBOT_LIST = db.Column(JSONB, comment='通知机器人列表')


class TTestplanExecutionItems(DBModel, BaseColumn):
    """测试计划执行记录项目明细表"""
    __tablename__ = 'TESTPLAN_EXECUTION_ITEMS'
    EXECUTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='执行编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='集合编号')
    SORT_NO = db.Column(db.Integer, nullable=False, comment='序号')
    RUNNING_STATE = db.Column(db.String(64), comment='运行状态，待运行/运行中/已完成')
    ITERATION_COUNT = db.Column(db.Integer, nullable=False, default=0, comment='迭代次数')
    SUCCESS_COUNT = db.Column(db.Integer, nullable=False, default=0, comment='成功次数')
    FAILURE_COUNT = db.Column(db.Integer, nullable=False, default=0, comment='失败次数')
    ERROR_COUNT = db.Column(db.Integer, nullable=False, default=0, comment='异常次数')
    UniqueConstraint('EXECUTION_NO', 'COLLECTION_NO', 'DELETED', name='unique_execution_collection')


class TTestReport(DBModel, BaseColumn):
    """测试报告表"""
    __tablename__ = 'TEST_REPORT'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    PLAN_NO = db.Column(db.String(32), index=True, nullable=False, comment='计划编号')
    EXECUTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='执行编号')
    REPORT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='报告编号')
    REPORT_NAME = db.Column(db.String(256), nullable=False, comment='报告名称')
    REPORT_DESC = db.Column(db.String(512), comment='报告描述')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer, comment='耗时')
    UniqueConstraint('WORKSPACE_NO', 'PLAN_NO', 'REPORT_NO', 'DELETED', name='unique_workspace_plan_report')


class TTestCollectionResult(DBModel, BaseColumn):
    """测试集合结果表"""
    __tablename__ = 'TEST_COLLECTION_RESULT'
    REPORT_NO = db.Column(db.String(32), index=True, nullable=False, comment='报告编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='集合编号')
    COLLECTION_ID = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='运行时集合的对象id')
    COLLECTION_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    COLLECTION_REMARK = db.Column(db.String(512), comment='元素描述')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer, comment='耗时')
    SUCCESS = db.Column(db.Boolean, comment='是否成功')


class TTestGroupResult(DBModel, BaseColumn):
    """测试分组结果表"""
    __tablename__ = 'TEST_GROUP_RESULT'
    REPORT_NO = db.Column(db.String(32), index=True, nullable=False, comment='报告编号')
    COLLECTION_ID = db.Column(db.String(32), index=True, nullable=False, comment='运行时集合的对象id')
    GROUP_ID = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='运行时分组的对象id')
    GROUP_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    GROUP_REMARK = db.Column(db.String(512), comment='元素描述')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer, comment='耗时')
    SUCCESS = db.Column(db.Boolean, comment='是否成功')


class TTestSamplerResult(DBModel, BaseColumn):
    """测试取样器结果表"""
    __tablename__ = 'TEST_SAMPLER_RESULT'
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
    RETRYING = db.Column(db.Boolean, comment='重试中')
    REQUEST_URL = db.Column(db.Text, comment='请求地址')
    REQUEST_HEADERS = db.Column(db.Text, comment='请求头')
    REQUEST_DATA = db.Column(db.Text, comment='请求数据')
    RESPONSE_CODE = db.Column(db.Text, comment='响应码')
    RESPONSE_HEADERS = db.Column(db.Text, comment='响应头')
    RESPONSE_DATA = db.Column(db.Text, comment='响应数据')
    FAILED_ASSERTION = db.Column(db.Text, comment='失败断言数据')
