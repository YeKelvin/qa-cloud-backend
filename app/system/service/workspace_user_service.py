#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : workspace_user_service.py
# @Time    : 2021/6/5 23:39
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.system.dao import workspace_user_rel_dao as WorkspaceUserRelDao
from app.system.model import TWorkspaceUserRel
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def add_workspace_user(req):
    ...


@http_service
def modify_workspace_user(req):
    ...


@http_service
def remove_workspace_user(req):
    ...
