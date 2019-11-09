#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from datetime import datetime

from server.database import Model, db
from server.utils.log_util import get_logger

log = get_logger(__name__)


class TActionLog(Model):
    __tablename__ = 't_action_log'
    id = db.Column(db.Integer, primary_key=True)
    action_detail = db.Column(db.String(128))
    description = db.Column(db.String(128))
    created_time = db.Column(db.DateTime, default=datetime.now())
    created_by = db.Column(db.String(64))
    updated_time = db.Column(db.DateTime, default=datetime.now())
    updated_by = db.Column(db.String(64))
