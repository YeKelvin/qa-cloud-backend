#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
import hashlib
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from server.database import Model, db
from server.utils.log_util import get_logger

log = get_logger(__name__)


class TUser(Model):
    __tablename__ = 't_user'
    id = db.Column(db.Integer, primary_key=True)
    user_no = db.Column(db.Integer, index=True, unique=True, nullable=False, comment='用户编号')
    username = db.Column(db.String(128), nullable=False, comment='用户名')
    password_hash = db.Column(db.String(512), nullable=False, comment='密码')
    mobile_no = db.Column(db.String(64), comment='手机号')
    email = db.Column(db.String(128), comment='邮箱地址')
    state = db.Column(db.String(32), nullable=False, comment='用户状态')
    access_token = db.Column(db.String(512), comment='token')
    last_login_time = db.Column(db.DateTime, comment='最后登录时间')
    last_success_time = db.Column(db.DateTime, comment='最后成功登录时间')
    last_error_time = db.Column(db.DateTime, comment='最后失败登录时间')
    error_times = db.Column(db.Integer, comment='登录失败次数')
    remark = db.Column(db.String(128), comment='备注')
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, default=datetime.now(), comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = self.__generate_password_hash(password)

    def __generate_password_hash(self, password):
        prefix_md5 = self.username + hashlib.md5(password.encode('utf-8')).hexdigest()
        pwd_md5 = hashlib.md5(prefix_md5.encode('utf-8')).hexdigest()
        return generate_password_hash(pwd_md5)

    def check_password_hash(self, password):
        prefix_md5 = self.username + hashlib.md5(password.encode('utf-8')).hexdigest()
        pwd_md5 = hashlib.md5(prefix_md5.encode('utf-8')).hexdigest()
        return check_password_hash(self.password, pwd_md5)


class TRole(Model):
    __tablename__ = 't_role'
    id = db.Column(db.Integer, primary_key=True)
    role_no = db.Column(db.Integer, index=True, unique=True, nullable=False, comment='角色编号')
    role_name = db.Column(db.String(128), comment='角色名称')
    remark = db.Column(db.String(128), comment='备注')
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, default=datetime.now(), comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TUserRoleRel(Model):
    __tablename__ = 't_user_role_rel'
    id = db.Column(db.Integer, primary_key=True)
    user_no = db.Column(db.Integer, index=True, nullable=False, comment='用户编号')
    role_no = db.Column(db.Integer, nullable=False, comment='角色编号')
    remark = db.Column(db.String(128), comment='备注')
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, default=datetime.now(), comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TPermission(Model):
    __tablename__ = 't_permission'
    id = db.Column(db.Integer, primary_key=True)
    permission_no = db.Column(db.Integer, index=True, unique=True, nullable=False, comment='权限编号')
    permission_name = db.Column(db.String(128), nullable=False, comment='权限名称')
    module = db.Column(db.String(128), nullable=False, comment='路由模块')
    endpoint = db.Column(db.String(128), nullable=False, comment='路由路径')
    method = db.Column(db.String(128), nullable=False, comment='HTTP请求方法')
    remark = db.Column(db.String(128), comment='备注')
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, default=datetime.now(), comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TRolePermissionRel(Model):
    __tablename__ = 't_role_permission_rel'
    id = db.Column(db.Integer, primary_key=True)
    role_no = db.Column(db.Integer, index=True, nullable=False, comment='角色编号')
    permission_no = db.Column(db.Integer, nullable=False, comment='权限编号')
    remark = db.Column(db.String(128), comment='备注')
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, default=datetime.now(), comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TMenu(Model):
    __tablename__ = 't_menu'
    id = db.Column(db.Integer, primary_key=True)
    menu_no = db.Column(db.Integer, index=True, nullable=False, comment='菜单编号')
    menu_name = db.Column(db.String(128), nullable=False, comment='菜单名称')
    level = db.Column(db.Integer, nullable=False, comment='菜单层级')
    order = db.Column(db.Integer, nullable=False, comment='菜单顺序')
    parent_no = db.Column(db.Integer, nullable=False, comment='父级菜单')
    href = db.Column(db.String(128), nullable=False, comment='菜单链接')
    icon = db.Column(db.String(128), nullable=False, comment='菜单图标')
    state = db.Column(db.String(16), nullable=False, comment='菜单状态')
    remark = db.Column(db.String(128), comment='备注')
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, default=datetime.now(), comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')


class TRoleMenuRel(Model):
    __tablename__ = 't_role_menu_rel'
    id = db.Column(db.Integer, primary_key=True)
    role_no = db.Column(db.Integer, index=True, nullable=False, comment='角色编号')
    menu_no = db.Column(db.Integer, nullable=False, comment='菜单编号')
    remark = db.Column(db.String(128), comment='备注')
    created_time = db.Column(db.DateTime, comment='创建时间')
    created_by = db.Column(db.String(64), comment='创建人')
    updated_time = db.Column(db.DateTime, default=datetime.now(), comment='更新时间')
    updated_by = db.Column(db.String(64), comment='更新人')
