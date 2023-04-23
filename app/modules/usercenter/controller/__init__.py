#!/usr/bin/ python3
# @File    : __init__.py
# @Time    : 2020/3/17 15:36
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('usercenter', __name__, url_prefix='/usercenter')


from . import auth_controller               # noqa
from . import group_controller              # noqa
from . import permission_controller         # noqa
from . import role_controller               # noqa
from . import role_permission_controller    # noqa
from . import user_controller               # noqa
from . import user_role_controller          # noqa
