#!/usr/bin/ python3
# @File    : __init__.py
# @Time    : 2021-08-18 15:04:36
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('public', __name__, url_prefix='/public')


from . import message_controller                # noqa
from . import tag_controller                    # noqa
from . import workspace_controller              # noqa
from . import workspace_member_controller       # noqa
from . import workspace_restriction_controller  # noqa
