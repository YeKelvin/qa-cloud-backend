#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2023-04-17 17:14:19
# @Author  : Kelvin.Ye
from flask import Blueprint


# note  : /rest/api 由nginx代理，后端不需要处理
blueprint = Blueprint('openplatform', __name__, url_prefix='/openplatform')

from . import tpa_controller  # noqa
