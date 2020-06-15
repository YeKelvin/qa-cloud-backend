#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
import hashlib

from werkzeug.security import generate_password_hash, check_password_hash

from server.database import Model, db
from server.utils.log_util import get_logger

log = get_logger(__name__)


class TUser(Model):
    """用户表
    """
    __tablename__ = 'USER'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='乐观锁')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    USER_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='用户编号')
    USER_NAME = db.Column(db.String(128), nullable=False, comment='用户名称')
    MOBILE_NO = db.Column(db.String(16), comment='手机号')
    EMAIL = db.Column(db.String(128), comment='邮箱')
    AVATAR = db.Column(db.String(256), comment='头像URL')
    STATE = db.Column(db.String(16), nullable=False, comment='用户状态(ENABLE启用, CLOSE禁用)')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, comment='更新时间')


class TRole(Model):
    """角色表
    """
    __tablename__ = 'ROLE'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='乐观锁')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ROLE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='角色编号')
    ROLE_NAME = db.Column(db.String(128), comment='角色名称')
    ROLE_DESC = db.Column(db.String(256), comment='角色描述')
    STATE = db.Column(db.String(16), nullable=False, comment='角色状态(ENABLE启用, CLOSE禁用)')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, comment='更新时间')


class TUserRoleRel(Model):
    """用户角色关联表
    """
    __tablename__ = 'USER_ROLE_REL'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='乐观锁')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    USER_NO = db.Column(db.String(32), index=True, nullable=False, comment='用户编号')
    ROLE_NO = db.Column(db.String(32), nullable=False, comment='角色编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, comment='更新时间')


class TPermission(Model):
    """权限表
    """
    __tablename__ = 'PERMISSION'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='乐观锁')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    PERMISSION_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='权限编号')
    PERMISSION_NAME = db.Column(db.String(128), nullable=False, comment='权限名称')
    PERMISSION_DESC = db.Column(db.String(256), comment='权限描述')
    METHOD = db.Column(db.String(128), nullable=False, comment='HTTP请求方法')
    ENDPOINT = db.Column(db.String(128), nullable=False, comment='路由路径')
    STATE = db.Column(db.String(16), nullable=False, comment='权限状态(ENABLE启用, CLOSE禁用)')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, comment='更新时间')


class TRolePermissionRel(Model):
    """角色权限关联表
    """
    __tablename__ = 'ROLE_PERMISSION_REL'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='乐观锁')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ROLE_NO = db.Column(db.String(32), index=True, nullable=False, comment='角色编号')
    PERMISSION_NO = db.Column(db.String(32), nullable=False, comment='权限编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, comment='更新时间')


class TUserLoginInfo(Model):
    """用户登陆号表
    """
    __tablename__ = 'USER_LOGIN_INFO'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='乐观锁')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    USER_NO = db.Column(db.String(32), index=True, nullable=False, comment='用户编号')
    LOGIN_NAME = db.Column(db.String(64), index=True, nullable=False, comment='登录账号')
    LOGIN_TYPE = db.Column(db.String(32), nullable=False, comment='登陆类型(MOBILE:手机号,EMAIL:邮箱,ACCOUNT:账号)')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, comment='更新时间')


class TUserLoginLog(Model):
    """用户登陆日志表
    """
    __tablename__ = 'USER_LOGIN_LOG'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='乐观锁')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    USER_NO = db.Column(db.String(32), nullable=False, comment='用户编号')
    LOGIN_NAME = db.Column(db.String(64), nullable=False, comment='登录账号')
    LOGIN_TYPE = db.Column(db.String(32), comment='登陆类型(MOBILE:手机号,EMAIL:邮箱,ACCOUNT:账号)')
    IP = db.Column(db.String(256), comment='IP地址')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, comment='更新时间')


class TUserPassword(Model):
    """用户密码表
    """
    __tablename__ = 'USER_PASSWORD'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='乐观锁')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    USER_NO = db.Column(db.String(32), index=True, nullable=False, comment='用户编号')
    PASSWORD = db.Column(db.String(256), nullable=False, comment='密码')
    PASSWORD_TYPE = db.Column(db.String(16), nullable=False, comment='密码类型(LOGIN:登录密码)')
    LAST_SUCCESS_TIME = db.Column(db.DateTime, comment='最后一次密码校验成功时间')
    LAST_ERROR_TIME = db.Column(db.DateTime, comment='最后一次密码校验错误时间')
    ERROR_TIMES = db.Column(db.Integer, comment='密码错误次数')
    UNLOCK_TIME = db.Column(db.DateTime, comment='解锁时间')
    CREATE_TYPE = db.Column(db.String(16), nullable=False, comment='密码创建类型(CUSTOMER:客户设置, SYSTEM:系统生成)')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, comment='更新时间')

    def generate_password_hash(self, password):
        prefix_md5 = self.username + hashlib.md5(password.encode('utf-8')).hexdigest()
        pwd_md5 = hashlib.md5(prefix_md5.encode('utf-8')).hexdigest()
        return generate_password_hash(pwd_md5)

    def check_password_hash(self, password):
        prefix_md5 = self.username + hashlib.md5(password.encode('utf-8')).hexdigest()
        pwd_md5 = hashlib.md5(prefix_md5.encode('utf-8')).hexdigest()
        return check_password_hash(self.password, pwd_md5)


class TUserPasswordPublicKey(Model):
    """用户密码公钥表
    """
    __tablename__ = 'USER_PASSWORD_PUBLIC_KEY'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='乐观锁')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    USER_NO = db.Column(db.String(32), index=True, nullable=False, comment='用户编号')
    PASSWORD_TYPE = db.Column(db.String(16), nullable=False, comment='密码类型(LOGIN:登录密码)')
    PASSWORD_KEY = db.Column(db.String(128), nullable=False, comment='RSA公钥')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, comment='更新时间')


class TUserAccessToken(Model):
    """用户认证令牌表
    """
    __tablename__ = 'USER_ACCESS_TOKEN'
    ID = db.Column(db.Integer, primary_key=True)
    VERSION = db.Column(db.Integer, nullable=False, default=0, comment='乐观锁')
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    USER_NO = db.Column(db.String(32), index=True, nullable=False, comment='用户编号')
    LOGIN_NAME = db.Column(db.String(64), nullable=False, comment='登录账号')
    ACCESS_TOKEN = db.Column(db.String(512), nullable=False, comment='令牌')
    EXPIRE_IN = db.Column(db.DateTime, nullable=False, comment='令牌到期时间')
    STATE = db.Column(db.String(16), nullable=False, comment='令牌状态(VALID启用, INVALID禁用)')
    DEVICE_ID = db.Column(db.String(64), nullable=False, comment='设备ID')
    APP_ID = db.Column(db.String(64), nullable=False, comment='应用ID')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, comment='更新时间')
