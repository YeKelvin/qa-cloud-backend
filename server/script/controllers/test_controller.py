#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_controller.py
# @Time    : 2021/1/27 09:19
# @Author  : Kelvin.Ye
from server.common.parser import JsonParser, Argument
from server.script.controllers import blueprint
from server.script.services import test_service as service
from server.common.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/test/run', methods=['GET', 'POST'])
def test_run():
    req = JsonParser(
        Argument('elementNo')
    ).parse()
    return service.test_run(req)
