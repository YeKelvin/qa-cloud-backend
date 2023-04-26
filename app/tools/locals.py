#!/usr/bin/ python3
# @File    : locals.py
# @Time    : 2022/7/18 14:00
# @Author  : Kelvin.Ye
import os
from threading import local as ThreadLocal

from gevent.local import local as CoroutineLocal


threadlocal = ThreadLocal() if bool(os.environ.get('FLASK_DEBUG')) else CoroutineLocal()
