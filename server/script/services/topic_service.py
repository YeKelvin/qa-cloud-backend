#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : topic_service
# @Time    : 2020/3/13 16:56
# @Author  : Kelvin.Ye
from datetime import datetime

from server.librarys.decorators.service import http_service
from server.librarys.helpers.global_helper import Global
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.sequence import Sequence
from server.librarys.verify import Verify
from server.script.model import TTestTopic
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def topic_list(req: RequestDTO):
    """分页查询测试主题列表
    """
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = []
    if req.attr.topicNo:
        conditions.append(TTestTopic.topic_no == req.attr.topicNo)
    if req.attr.topicName:
        conditions.append(TTestTopic.topic_name.like(f'%{req.attr.topicName}%'))
    if req.attr.topicDescription:
        conditions.append(TTestTopic.topic_description.like(f'%{req.attr.topicDescription}%'))

    # 列表总数
    total_size = TTestTopic.query.filter(*conditions).count()

    # 列表数据
    topics = TTestTopic.query.filter(
        *conditions
    ).order_by(
        TTestTopic.created_time.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for topic in topics:
        data_set.append({
            'topicNo': topic.topic_no,
            'topicName': topic.topic_name,
            'topicDescription': topic.topic_description
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def topic_all(req: RequestDTO):
    """查询所有测试主题
    """
    topics = TTestTopic.query.order_by(TTestTopic.created_time.desc()).all()
    result = []
    for topic in topics:
        result.append({
            'topicNo': topic.topic_no,
            'topicName': topic.topic_name,
            'topicDescription': topic.topic_description
        })
    return result


@http_service
def create_topic(req: RequestDTO):
    """新增测试主题
    """
    topic = TTestTopic.query.filter_by(topic_name=req.attr.topicName).first()
    Verify.empty(topic, '测试主题已存在')

    TTestTopic.create(
        topic_no=generate_topic_no(),
        topic_name=req.attr.topicName,
        topic_description=req.attr.topicDescription,
        created_by=Global.operator,
        created_time=datetime.now(),
        updated_by=Global.operator,
        updated_time=datetime.now()
    )
    return None


@http_service
def modify_topic(req: RequestDTO):
    """修改测试主题
    """
    topic = TTestTopic.query.filter_by(topic_no=req.attr.topicNo).first()
    Verify.not_empty(topic, '测试主题不存在')

    if req.attr.topicName:
        topic.topic_name = req.attr.topicName
    if req.attr.topicDescription:
        topic.topic_description = req.attr.topicDescription

    topic.save()
    return None


@http_service
def delete_topic(req: RequestDTO):
    """删除测试主题
    """
    topic = TTestTopic.query.filter_by(topic_no=req.attr.topicNo).first()
    Verify.not_empty(topic, '测试主题不存在')

    topic.delete()
    return None


def generate_topic_no():
    seq_topic_no = Sequence('seq_topic_no')
    return 'topic' + str(seq_topic_no.next_value()).zfill(8)
