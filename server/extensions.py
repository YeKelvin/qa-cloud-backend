#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : extensions.py
# @Time    : 2019/11/7 10:56
# @Author  : Kelvin.Ye
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from server.utils.log_util import get_logger

log = get_logger(__name__)
db = SQLAlchemy()
swagger = Swagger()
