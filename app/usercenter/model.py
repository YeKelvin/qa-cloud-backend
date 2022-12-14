#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from sqlalchemy.dialects.postgresql import JSONB

from app.database import BaseColumn
from app.database import DBModel
from app.database import db


class TUser(DBModel, BaseColumn):
    """用户表"""
    __tablename__ = 'USER'
    USER_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='用户编号')
    USER_NAME = db.Column(db.String(128), nullable=False, comment='用户名称')
    MOBILE_NO = db.Column(db.String(16), comment='手机号')
    EMAIL = db.Column(db.String(128), comment='邮箱')
    AVATAR = db.Column(db.String(256), comment='头像URL')
    STATE = db.Column(db.String(16), nullable=False, default='ENABLE', comment='用户状态(ENABLE:启用, DISABLE:禁用)')
    LOGGED_IN = db.Column(db.Boolean, nullable=False, default=False, comment='是否已登录')


class TGroup(DBModel, BaseColumn):
    __tablename__ = 'GROUP'
    GROUP_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='分组编号')
    GROUP_NAME = db.Column(db.String(128), nullable=False, comment='分组名称')
    GROUP_DESC = db.Column(db.String(128), nullable=False, comment='分组描述')
    STATE = db.Column(db.String(16), nullable=False, default='ENABLE', comment='分组状态(ENABLE:启用, DISABLE:禁用)')


class TRole(DBModel, BaseColumn):
    """角色表"""
    __tablename__ = 'ROLE'
    ROLE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='角色编号')
    ROLE_NAME = db.Column(db.String(128), nullable=False, comment='角色名称')
    ROLE_DESC = db.Column(db.String(256), comment='角色描述')
    ROLE_CODE = db.Column(db.String(64), unique=True, nullable=False, comment='角色代码')
    ROLE_RANK = db.Column(db.Integer, nullable=False, default=1, comment='角色等级')
    ROLE_TYPE = db.Column(db.String(64), comment='角色类型(SYSTEM:系统内置, CUSTOM:自定义)')
    STATE = db.Column(db.String(16), nullable=False, default='ENABLE', comment='角色状态(ENABLE:启用, DISABLE:禁用)')


class TPermission(DBModel, BaseColumn):
    """权限表"""
    __tablename__ = 'PERMISSION'
    MODULE_NO = db.Column(db.String(32), index=True, nullable=False, comment='模块编号')
    OBJECT_NO = db.Column(db.String(32), index=True, nullable=False, comment='对象编号')
    PERMISSION_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='权限编号')
    PERMISSION_NAME = db.Column(db.String(128), nullable=False, comment='权限名称')
    PERMISSION_DESC = db.Column(db.String(256), comment='权限描述')
    PERMISSION_CODE = db.Column(db.String(64), unique=True, nullable=False, comment='权限代码')
    PERMISSION_ACT = db.Column(db.String(64), comment='权限行为，增删改查等')
    STATE = db.Column(db.String(16), nullable=False, default='ENABLE', comment='权限状态(ENABLE:启用, DISABLE:禁用)')


class TUserGroup(DBModel, BaseColumn):
    __tablename__ = 'USER_GROUP'
    USER_NO = db.Column(db.String(32), index=True, nullable=False, comment='用户编号')
    GROUP_NO = db.Column(db.String(32), index=True, nullable=False, comment='分组编号')


class TUserRole(DBModel, BaseColumn):
    """用户角色关联表"""
    __tablename__ = 'USER_ROLE'
    USER_NO = db.Column(db.String(32), index=True, nullable=False, comment='用户编号')
    ROLE_NO = db.Column(db.String(32), index=True, nullable=False, comment='角色编号')


class TGroupRole(DBModel, BaseColumn):
    __tablename__ = 'GROUP_ROLE'
    GROUP_NO = db.Column(db.String(32), index=True, nullable=False, comment='分组编号')
    ROLE_NO = db.Column(db.String(32), index=True, nullable=False, comment='角色编号')


class TRolePermission(DBModel, BaseColumn):
    """角色权限关联表"""
    __tablename__ = 'ROLE_PERMISSION'
    ROLE_NO = db.Column(db.String(32), index=True, nullable=False, comment='角色编号')
    PERMISSION_NO = db.Column(db.String(32), index=True, nullable=False, comment='权限编号')


class TUserLoginInfo(DBModel, BaseColumn):
    """用户登陆号表"""
    __tablename__ = 'USER_LOGIN_INFO'
    USER_NO = db.Column(db.String(32), index=True, nullable=False, comment='用户编号')
    LOGIN_NAME = db.Column(db.String(64), index=True, nullable=False, comment='登录账号')
    LOGIN_TYPE = db.Column(db.String(32), nullable=False, comment='登陆类型(MOBILE:手机号, EMAIL:邮箱, ACCOUNT:账号)')


class TUserLoginLog(DBModel, BaseColumn):
    """用户登陆日志表"""
    __tablename__ = 'USER_LOGIN_LOG'
    USER_NO = db.Column(db.String(32), index=True, nullable=False, comment='用户编号')
    LOGIN_NAME = db.Column(db.String(64), nullable=False, comment='登录账号')
    LOGIN_TYPE = db.Column(db.String(32), comment='登陆类型(MOBILE:手机号, EMAIL:邮箱, ACCOUNT:账号)')
    IP = db.Column(db.String(256), comment='IP地址')


class TUserPassword(DBModel, BaseColumn):
    """用户密码表"""
    __tablename__ = 'USER_PASSWORD'
    USER_NO = db.Column(db.String(32), index=True, nullable=False, comment='用户编号')
    PASSWORD = db.Column(db.String(256), nullable=False, comment='密码')
    PASSWORD_TYPE = db.Column(db.String(16), nullable=False, comment='密码类型(LOGIN:登录密码)')
    LAST_SUCCESS_TIME = db.Column(db.DateTime, comment='最后一次密码校验成功时间')
    LAST_ERROR_TIME = db.Column(db.DateTime, comment='最后一次密码校验错误时间')
    ERROR_TIMES = db.Column(db.Integer, default=0, comment='密码错误次数')
    UNLOCK_TIME = db.Column(db.DateTime, comment='解锁时间')
    CREATE_TYPE = db.Column(db.String(16), nullable=False, comment='密码创建类型(CUSTOMER:客户设置, SYSTEM:系统生成)')


class TUserSecretKey(DBModel, BaseColumn):
    """用户密钥表"""
    # TODO: 单机读内存，集群读redis
    __tablename__ = 'USER_SECRET_KEY'
    INDEX = db.Column(db.String(128), index=True, nullable=False, comment='索引编号')
    DATA = db.Column(db.Text, nullable=False, comment='密钥')


class TPermissionModule(DBModel, BaseColumn):
    """权限模块表"""
    __tablename__ = 'PERMISSION_MODULE'
    MODULE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='模块编号')
    MODULE_NAME = db.Column(db.String(128), nullable=False, comment='模块名称')
    MODULE_DESC = db.Column(db.String(256), comment='模块描述')
    MODULE_CODE = db.Column(db.String(64), unique=True, nullable=False, comment='模块代码')


class TPermissionObject(DBModel, BaseColumn):
    """权限对象表"""
    __tablename__ = 'PERMISSION_OBJECT'
    OBJECT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='对象编号')
    OBJECT_NAME = db.Column(db.String(128), nullable=False, comment='对象名称')
    OBJECT_DESC = db.Column(db.String(256), comment='对象描述')
    OBJECT_CODE = db.Column(db.String(64), unique=True, nullable=False, comment='对象代码')


class TUserSettings(DBModel, BaseColumn):
    """用户设置表"""
    __tablename__ = 'USER_SETTINGS'
    USER_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='用户编号')
    DATA = db.Column(JSONB, comment='用户设置')
