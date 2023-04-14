#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2021-08-18 15:04:36
# @Author  : Kelvin.Ye
from flask import Blueprint


# note  : /rest/api 由nginx代理，后端不需要处理
blueprint = Blueprint('public', __name__, url_prefix='/public')

from . import message_controller  # noqa
from . import tag_controller  # noqa
from . import workspace_controller  # noqa
from . import workspace_restriction_controller  # noqa
from . import workspace_user_controller  # noqa
