#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : __init__.py
# @Time    : 2020/3/13 16:53
# @Author  : Kelvin.Ye
from flask import Blueprint

blueprint = Blueprint('script', __name__, url_prefix='/script')

from . import element_package_route
from . import element_route
from . import env_var_route
from . import http_header_route
from . import workspace_route
from . import topic_route
