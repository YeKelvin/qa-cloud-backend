#!/usr/bin/ python3
# @File    : __init__.py
# @Time    : 2022/5/13 14:47
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('schedule', __name__, url_prefix='/schedule')


from . import job_controller    # noqa
