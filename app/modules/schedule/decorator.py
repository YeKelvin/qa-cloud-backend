#!/usr/bin python3
# @Module  : schedule
# @File    : decorator.py
# @Time    : 2024-03-18 16:44:49
# @Author  : Kelvin.Ye
from functools import wraps

from app.extension import apscheduler


def apscheduler_app_context(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        with apscheduler.app.app_context():
            return func(*args, **kwargs)

    return wrapper
