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
    user_no = db.Column(db.Integer, index=True, unique=True, nullable=False)
    username = db.Column(db.String(128))
    password = db.Column(db.String(128))
    mobile_no = db.Column(db.String(64))
    email = db.Column(db.String(128))
    status = db.Column(db.String(32))
    last_login_time = db.Column(db.DateTime)
    last_success_time = db.Column(db.DateTime)
    last_error_time = db.Column(db.DateTime)
    error_times = db.Column(db.Integer)
    description = db.Column(db.String(128))
    created_time = db.Column(db.DateTime, default=datetime.now())
    created_by = db.Column(db.String(64))
    updated_time = db.Column(db.DateTime, default=datetime.now())
    updated_by = db.Column(db.String(64))

    def generate_password_hash(self, password: str):
        prefix_md5 = self.username + hashlib.md5(password.encode('utf-8')).hexdigest()
        pwd_md5 = hashlib.md5(prefix_md5.encode('utf-8')).hexdigest()
        return generate_password_hash(pwd_md5)

    def check_password_hash(self, password):
        return check_password_hash(self.password, password)


class TRole(Model):
    __tablename__ = 't_role'
    id = db.Column(db.Integer, primary_key=True)
    role_no = db.Column(db.Integer, index=True, nullable=False)
    permissions = db.Column(db.String(256))
    description = db.Column(db.String(128))
    created_time = db.Column(db.DateTime, default=datetime.now())
    created_by = db.Column(db.String(64))
    updated_time = db.Column(db.DateTime, default=datetime.now())
    updated_by = db.Column(db.String(64))


class TPermission(Model):
    __tablename__ = 't_permission'
    id = db.Column(db.Integer, primary_key=True)
    permission_no = db.Column(db.Integer, index=True, nullable=False)
    endpoint = db.Column(db.String(128))
    description = db.Column(db.String(128))
    created_time = db.Column(db.DateTime, default=datetime.now())
    created_by = db.Column(db.String(64))
    updated_time = db.Column(db.DateTime, default=datetime.now())
    updated_by = db.Column(db.String(64))


class TUserRoleRelation(Model):
    __tablename__ = 't_user_role_relation'
    id = db.Column(db.Integer, primary_key=True)
    user_no = db.Column(db.Integer, index=True, nullable=False)
    role_no = db.Column(db.Integer, index=True, nullable=False)
    description = db.Column(db.String(128))
    created_time = db.Column(db.DateTime, default=datetime.now())
    created_by = db.Column(db.String(64))
    updated_time = db.Column(db.DateTime, default=datetime.now())
    updated_by = db.Column(db.String(64))
