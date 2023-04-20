#!/usr/bin/ python3
# @File    : controller.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from flask import Blueprint


blueprint = Blueprint('filecenter', __name__, url_prefix='/filecenter')


@blueprint.post('/upload')
def upload():
    pass


@blueprint.get('/download')
def download():
    pass
