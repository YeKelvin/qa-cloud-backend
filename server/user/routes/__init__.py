#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2020/3/17 15:36
# @Author  : Kelvin.Ye
from flask import Blueprint

blueprint = Blueprint('user', __name__, url_prefix='/user')
blueprint2 = Blueprint('user2', __name__, url_prefix='/rest/api/1/user')

from . import security_route
from . import user_route
from . import role_route
from . import permission_route
from . import user_role_route
from . import role_permission_route
