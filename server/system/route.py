#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : route.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from flask import Blueprint

from server.utils.log_util import get_logger

log = get_logger(__name__)

blueprint = Blueprint('system', __name__, url_prefix='/system')
