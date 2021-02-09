#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2020/3/17 15:36
# @Author  : Kelvin.Ye
from flask import Blueprint

blueprint = Blueprint('user', __name__, url_prefix='/user')

from . import auth_controller
from . import user_controller
from . import role_controller
from . import permission_controller
from . import user_role_controller
from . import role_permission_controller
