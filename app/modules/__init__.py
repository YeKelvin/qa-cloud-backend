#!/usr/bin python3
# @Module  : modules
# @File    : __init__.py
# @Time    : 2023-04-19 11:57:49
# @Author  : Kelvin.Ye
from flask import Blueprint


restapi = Blueprint('restapi', __name__)


# 加载子路由
# from .filecenter.controller import blueprint as filecenter_blueprint
from .opencenter.controller import blueprint as opencenter_blueprint    # noqa
from .public.controller import blueprint as public_blueprint            # noqa
from .schedule.controller import blueprint as schedule_blueprint        # noqa
from .script.controller import blueprint as script_blueprint            # noqa
from .system.controller import blueprint as system_blueprint            # noqa
from .usercenter.controller import blueprint as usercenter_blueprint    # noqa


# 注册子路由
# restapi.register_blueprint(filecenter_blueprint)
restapi.register_blueprint(opencenter_blueprint)
restapi.register_blueprint(public_blueprint)
restapi.register_blueprint(schedule_blueprint)
restapi.register_blueprint(script_blueprint)
restapi.register_blueprint(system_blueprint)
restapi.register_blueprint(usercenter_blueprint)
