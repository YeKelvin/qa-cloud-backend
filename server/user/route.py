#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : route.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from flask import Blueprint, request

from server.utils.log_util import get_logger

log = get_logger(__name__)

blueprint = Blueprint('user', __name__, url_prefix='/user')


@blueprint.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')


@blueprint.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')


@blueprint.route('/logout', methods=['POST'])
def logout():
    pass


@blueprint.route('/info', methods=['get'])
def info():
    pass
