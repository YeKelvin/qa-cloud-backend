#!/usr/bin/ python3
# @File    : model.py
# @Time    : 2021-08-18 15:27:03
# @Author  : Kelvin.Ye
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from app.database import BaseColumn
from app.database import DBModel
from app.database import db


class TWorkspace(DBModel, BaseColumn):
    """工作空间表"""
    __tablename__ = 'WORKSPACE'
    WORKSPACE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='空间编号')
    WORKSPACE_NAME = db.Column(db.String(128), nullable=False, comment='空间名称')
    WORKSPACE_SCOPE = db.Column(db.String(128), nullable=False, comment='空间作用域')
    WORKSPACE_DESC = db.Column(db.String(256), comment='空间描述')
    UniqueConstraint('WORKSPACE_NAME', 'WORKSPACE_SCOPE', 'DELETED', name='unique_name_type_scope')


class TWorkspaceUser(DBModel, BaseColumn):
    """空间用户表"""
    __tablename__ = 'WORKSPACE_USER'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    USER_NO = db.Column(db.String(32), index=True, nullable=False, comment='用户编号')
    UniqueConstraint('WORKSPACE_NO', 'USER_NO', 'DELETED', name='unique_workspace_user')


class TWorkspaceRestriction(DBModel, BaseColumn):
    """空间限制表"""
    __tablename__ = 'WORKSPACE_RESTRICTION'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    PERMISSION_NO = db.Column(db.String(32), index=True, nullable=False, comment='权限编号')


class TWorkspaceRestrictionExemption(DBModel, BaseColumn):
    """空间限制豁免表"""
    __tablename__ = 'WORKSPACE_RESTRICTION_EXEMPTION'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    USER_NUMBERS = db.Column(JSONB, comment='豁免用户编号列表')
    GROUP_NUMBERS = db.Column(JSONB, comment='豁免分组编号列表')


class TTag(DBModel, BaseColumn):
    """标签表"""
    __tablename__ = 'TAG'
    TAG_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='标签编号')
    TAG_NAME = db.Column(db.String(256), nullable=False, comment='标签名称')
    TAG_DESC = db.Column(db.String(256), nullable=False, comment='标签描述')
    UniqueConstraint('TAG_NAME', 'DELETED', name='unique_tagname')


class TNotificationRobot(DBModel, BaseColumn):
    """通知机器人表"""
    __tablename__ = 'NOTIFICATION_ROBOT'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    ROBOT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='机器人编号')
    ROBOT_NAME = db.Column(db.String(128), nullable=False, comment='机器人名称')
    ROBOT_DESC = db.Column(db.String(256), comment='机器人描述')
    ROBOT_TYPE = db.Column(db.String(16), nullable=False, comment='机器人类型(WECHAT, WECOM, DINGTALK)')
    ROBOT_CONFIG = db.Column(JSONB, comment='机器人配置')
    STATE = db.Column(db.String(16), nullable=False, default='ENABLE', comment='机器人状态(ENABLE:启用, DISABLE:禁用)')
