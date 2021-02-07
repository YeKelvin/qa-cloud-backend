#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2020/3/13 16:53
# @Author  : Kelvin.Ye
from flask import Blueprint

blueprint = Blueprint('script', __name__, url_prefix='/script')

from . import element_controller
from . import element_package_controller
from . import execution_controller
from . import env_var_controller
from . import http_header_controller
from . import workspace_controller
from . import topic_controller
from . import test_controller
