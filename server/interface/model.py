#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from server.database import Model, db
from server.utils.log_util import get_logger

log = get_logger(__name__)


class TTestItem(Model):
    __tablename__ = 't_test_item'
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TItemTopicRel(Model):
    __tablename__ = 't_item_topic_rel'
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TTestTopic(Model):
    __tablename__ = 't_test_topic'
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TTopicCollectionRel(Model):
    __tablename__ = 't_topic_collection_rel'
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TTestElement(Model):
    __tablename__ = 't_test_element'
    id = db.Column(db.Integer, primary_key=True)
    element_id = db.Column(db.Integer, index=True, unique=True, nullable=False, comment='节点ID')
    name = db.Column(db.String(512), nullable=False, comment='节点名称')
    comments = db.Column(db.String(512), nullable=False, comment='节点描述')
    type = db.Column(db.String(64), nullable=False, comment='节点类型', name='class')
    enabled = db.Column(db.Boolean, nullable=False, comment='是否启用')
    property = db.Column(db.JSON, nullable=False, comment='节点属性')
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TTestElementChildRel(Model):
    __tablename__ = 't_test_element_child_rel'
    id = db.Column(db.Integer, primary_key=True)
    element_id = db.Column(db.Integer, index=True, nullable=False, comment='节点ID')
    child_order = db.Column(db.Integer, nullable=False, comment='序号')
    child_id = db.Column(db.Integer, index=True, nullable=False, comment='子代ID')
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TEnvironmentVariable(Model):
    __tablename__ = 't_environment_variable'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(256), nullable=False, comment='变量名称')
    value = db.Column(db.String(512), nullable=False, comment='变量值')
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class THttpHeader(Model):
    __tablename__ = 't_http_header'
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TSQLConfiguration(Model):
    __tablename__ = 't_sql_configuration'
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TActionPackage(Model):
    __tablename__ = 't_action_package'
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')
