#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from server.database import Model, db
from server.utils.log_util import get_logger

log = get_logger(__name__)


class TTestItem(Model):
    """测试项目表
    """
    __tablename__ = 't_test_item'
    id = db.Column(db.Integer, primary_key=True)
    item_no = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='项目编号')
    item_name = db.Column(db.String(128), nullable=False, comment='项目名称')
    item_description = db.Column(db.String(256), comment='项目描述')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class TItemTopicRel(Model):
    """项目主题关联表
    """
    __tablename__ = 't_item_topic_rel'
    id = db.Column(db.Integer, primary_key=True)
    item_no = db.Column(db.String(32), nullable=False, comment='项目编号')
    topic_no = db.Column(db.String(32), nullable=False, comment='主题编号')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class TTestTopic(Model):
    """测试主题表
    """
    __tablename__ = 't_test_topic'
    id = db.Column(db.Integer, primary_key=True)
    topic_no = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='主题编号')
    topic_name = db.Column(db.String(128), nullable=False, comment='主题名称')
    topic_description = db.Column(db.String(256), comment='主题描述')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class TTopicCollectionRel(Model):
    """主题集合关联表
    """
    __tablename__ = 't_topic_collection_rel'
    id = db.Column(db.Integer, primary_key=True)
    topic_no = db.Column(db.String(32), nullable=False, comment='主题编号')
    collection_no = db.Column(db.String(32), nullable=False, comment='测试集合编号')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class TTestElement(Model):
    """测试元素表
    """
    __tablename__ = 't_test_element'
    id = db.Column(db.Integer, primary_key=True)
    element_no = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='元素编号')
    element_name = db.Column(db.String(256), nullable=False, comment='元素名称')
    element_comments = db.Column(db.String(512), nullable=False, comment='元素描述')
    element_type = db.Column(db.String(64), nullable=False, comment='元素类型')
    enabled = db.Column(db.Boolean, nullable=False, comment='是否启用')
    property = db.Column(db.JSON, nullable=False, comment='元素属性')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class TElementChildRel(Model):
    """元素子代关联表
    """
    __tablename__ = 't_element_child_rel'
    id = db.Column(db.Integer, primary_key=True)
    element_no = db.Column(db.String(32), nullable=False, comment='元素编号')
    child_order = db.Column(db.Integer, nullable=False, comment='子代序号')
    child_no = db.Column(db.String(32), index=True, nullable=False, comment='子代编号')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class TEnvironmentVariableCollection(Model):
    """环境变量集合表
    """
    __tablename__ = 't_environment_variable_collection'
    id = db.Column(db.Integer, primary_key=True)
    collection_no = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='环境集合编号')
    collection_name = db.Column(db.String(128), nullable=False, comment='环境集合名称')
    collection_description = db.Column(db.String(256), comment='环境集合描述')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class TEnvironmentVariableCollectionRel(Model):
    """环境变量集合关联表
    """
    __tablename__ = 't_environment_variable_collection_rel'
    id = db.Column(db.Integer, primary_key=True)
    collection_no = db.Column(db.String(32), nullable=False, comment='环境集合编号')
    env_no = db.Column(db.String(32), nullable=False, comment='环境变量编号')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class TEnvironmentVariable(Model):
    """环境变量表
    """
    __tablename__ = 't_environment_variable'
    id = db.Column(db.Integer, primary_key=True)
    env_no = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='环境变量编号')
    env_key = db.Column(db.String(256), nullable=False, comment='环境变量名称')
    env_value = db.Column(db.String(512), nullable=False, comment='环境变量值')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class THttpHeaderCollection:
    """HTTP头部集合表
    """
    __tablename__ = 't_http_header_collection'
    id = db.Column(db.Integer, primary_key=True)
    collection_no = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='头部集合编号')
    collection_name = db.Column(db.String(128), nullable=False, comment='头部集合名称')
    collection_description = db.Column(db.String(256), comment='头部集合描述')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class THttpHeaderCollectionRel:
    """HTTP头部集合关联表
    """
    __tablename__ = 't_http_header_collection_rel'
    id = db.Column(db.Integer, primary_key=True)
    collection_no = db.Column(db.String(32), nullable=False, comment='头部集合编号')
    header_no = db.Column(db.String(32), nullable=False, comment='头部编号')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class THttpHeader(Model):
    """HTTP头部表
    """
    __tablename__ = 't_http_header'
    id = db.Column(db.Integer, primary_key=True)
    header_no = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='头部编号')
    header_key = db.Column(db.String(256), nullable=False, comment='头部名称')
    header_value = db.Column(db.String(1024), nullable=False, comment='头部值')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class TSQLConfiguration(Model):
    """SQL配置表
    """
    __tablename__ = 't_sql_configuration'
    id = db.Column(db.Integer, primary_key=True)
    config_no = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='配置编号')
    config_name = db.Column(db.String(256), nullable=False, comment='配置名称')
    config_description = db.Column(db.String(256), nullable=False, comment='配置描述')
    connection_variable_name = db.Column(db.String(256), nullable=False, comment='数据库连接变量')
    db_type = db.Column(db.String(64), nullable=False, comment='数据库类型')
    db_url = db.Column(db.String(256), nullable=False, comment='数据库地址')
    username = db.Column(db.String(256), nullable=False, comment='数据库用户名称')
    password = db.Column(db.String(256), nullable=False, comment='数据库密码')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')


class TActionPackage(Model):
    """动作封装表
    """
    __tablename__ = 't_action_package'
    id = db.Column(db.Integer, primary_key=True)
    action_no = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='动作封装编号')
    collection_no = db.Column(db.String(32), nullable=False, comment='测试集合编号')
    created_by = db.Column(db.String(64), comment='创建人')
    created_time = db.Column(db.DateTime, comment='创建时间')
    updated_by = db.Column(db.String(64), comment='更新人')
    updated_time = db.Column(db.DateTime, comment='更新时间')
