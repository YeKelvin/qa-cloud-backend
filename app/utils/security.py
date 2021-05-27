#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : security
# @Time    : 2020/6/30 15:01
# @Author  : Kelvin.Ye
import hashlib

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash


def encrypt_password(login_name, password):
    prefix_md5 = login_name + hashlib.md5(password.encode('utf-8')).hexdigest()
    pwd_md5 = hashlib.md5(prefix_md5.encode('utf-8')).hexdigest()
    return generate_password_hash(pwd_md5)


def check_password(login_name, source_pwd, in_pwd):
    prefix_md5 = login_name + hashlib.md5(in_pwd.encode('utf-8')).hexdigest()
    pwd_md5 = hashlib.md5(prefix_md5.encode('utf-8')).hexdigest()
    return check_password_hash(source_pwd, pwd_md5)
