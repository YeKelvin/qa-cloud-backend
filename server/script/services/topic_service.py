#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : topic_service
# @Time    : 2020/3/13 16:56
# @Author  : Kelvin.Ye
from datetime import datetime

from server.common.number_generator import generate_topic_no
from server.librarys.decorators.service import http_service
from server.librarys.helpers.global_helper import Global
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.verify import Verify
from server.script.model import TTestTopic
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_topic_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    if req.attr.topicNo:
        conditions.append(TTestTopic.TOPIC_NO.like(f'%{req.attr.topicNo}%'))
    if req.attr.topicName:
        conditions.append(TTestTopic.TOPIC_NAME.like(f'%{req.attr.topicName}%'))
    if req.attr.topicDesc:
        conditions.append(TTestTopic.TOPIC_DESC.like(f'%{req.attr.topicDesc}%'))

    # 列表总数
    total_size = TTestTopic.query.filter(*conditions).count()

    # 列表数据
    topics = TTestTopic.query.filter(
        *conditions
    ).order_by(TTestTopic.CREATED_TIME.desc()).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for topic in topics:
        data_set.append({
            'topicNo': topic.TOPIC_NO,
            'topicName': topic.TOPIC_NAME,
            'topicDesc': topic.TOPIC_DESC
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def query_topic_all():
    topics = TTestTopic.query.order_by(TTestTopic.CREATED_TIME.desc()).all()
    result = []
    for topic in topics:
        result.append({
            'topicNo': topic.TOPIC_NO,
            'topicName': topic.TOPIC_NAME,
            'topicDesc': topic.TOPIC_DESC
        })
    return result


@http_service
def create_topic(req: RequestDTO):
    topic = TTestTopic.query.filter_by(TOPIC_NAME=req.attr.topicName).first()
    Verify.empty(topic, '测试主题已存在')

    TTestTopic.create(
        TOPIC_NO=generate_topic_no(),
        TOPIC_NAME=req.attr.topicName,
        TOPIC_DESC=req.attr.topicDesc,
        CREATED_BY=Global.operator,
        CREATED_TIME=datetime.now(),
        UPDATED_BY=Global.operator,
        UPDATED_TIME=datetime.now()
    )
    return None


@http_service
def modify_topic(req: RequestDTO):
    topic = TTestTopic.query.filter_by(TOPIC_NO=req.attr.topicNo).first()
    Verify.not_empty(topic, '测试主题不存在')

    if req.attr.topicName is not None:
        topic.TOPIC_NAME = req.attr.topicName
    if req.attr.topicDesc is not None:
        topic.TOPIC_DESC = req.attr.topicDesc

    topic.save()
    return None


@http_service
def delete_topic(req: RequestDTO):
    topic = TTestTopic.query.filter_by(TOPIC_NO=req.attr.topicNo).first()
    Verify.not_empty(topic, '测试主题不存在')

    topic.delete()
    return None


@http_service
def add_topic_collection(req: RequestDTO):
    pass


@http_service
def modify_topic_collection(req: RequestDTO):
    pass


@http_service
def remove_topic_collection(req: RequestDTO):
    pass
