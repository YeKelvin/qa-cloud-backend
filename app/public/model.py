#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2021-08-18 15:27:03
# @Author  : Kelvin.Ye
from sqlalchemy import UniqueConstraint

from app.database import BaseColumn
from app.database import DBModel
from app.database import db
from app.utils.log_util import get_logger


log = get_logger(__name__)


class TWorkspace(DBModel, BaseColumn):
    """工作空间表"""
    __tablename__ = 'WORKSPACE'
    WORKSPACE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='工作空间编号')
    WORKSPACE_NAME = db.Column(db.String(128), nullable=False, comment='工作空间名称')
    WORKSPACE_SCOPE = db.Column(db.String(128), nullable=False, comment='工作空间作用域')
    WORKSPACE_DESC = db.Column(db.String(256), comment='工作空间描述')
    UniqueConstraint('WORKSPACE_NAME', 'WORKSPACE_SCOPE', 'DELETED', name='unique_name_type_scope')


class TWorkspaceUserRel(DBModel, BaseColumn):
    """工作空间用户关联表"""
    __tablename__ = 'WORKSPACE_USER_REL'
    WORKSPACE_NO = db.Column(db.String(32), nullable=False, comment='工作空间编号')
    USER_NO = db.Column(db.String(32), nullable=False, comment='用户编号')
    UniqueConstraint('WORKSPACE_NO', 'USER_NO', 'DELETED', name='unique_workspace_user')


class TTag(DBModel, BaseColumn):
    """标签表"""
    __tablename__ = 'TAG'
    TAG_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='标签编号')
    TAG_NAME = db.Column(db.String(256), nullable=False, comment='标签名称')
    TAG_DESC = db.Column(db.String(256), nullable=False, comment='标签描述')
    UniqueConstraint('TAG_NAME', 'DELETED', name='unique_tagname')
