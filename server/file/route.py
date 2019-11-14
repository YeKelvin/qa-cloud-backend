#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : route.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from flask import Blueprint

from server.utils.log_util import get_logger

log = get_logger(__name__)

blueprint = Blueprint('file', __name__, url_prefix='/file')


@blueprint.route('/upload', methods=['POST'])
def upload():
    pass


@blueprint.route('/download', methods=['GET'])
def download():
    pass
