#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : wecom.py
# @Time    : 2022-05-08 15:13:18
# @Author  : Kelvin.Ye
import requests

from app.utils.json_util import to_json
from app.utils.log_util import get_logger


log = get_logger(__name__)


webhookurl = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='
headers = {'content-type': 'application/json'}
encoding = 'utf-8'


def text_message(key, content: str, mentioned_list: list = None, mentioned_mobile_list: list = None):
    """发送文本消息

    Args:
        content (str): 文本内容，最长不超过2048个字节，必须是utf8编码
        mentioned_list (list): userid的列表，提醒群中的指定成员(@某个成员)，@all表示提醒所有人，如果开发者获取不到userid，可以使用mentioned_mobile_list
        mentioned_mobile_list (list): 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
    """
    data = {
        'msgtype': 'text',
        'text': {
            'content': content,
            'mentioned_list': mentioned_list or [],
            'mentioned_mobile_list': mentioned_mobile_list or []
        }
    }
    res = requests.post(url=f'{webhookurl}{key}', headers=headers, data=to_json(data).encode(encoding=encoding))
    res.status_code != 200 and log.error(f'发送企业微信通知失败，接口响应: {res.text}')


def markdown_message(key, content: str):
    """发送markdown消息

    Args:
        content (str): markdown内容，最长不超过4096个字节，必须是utf8编码
    """
    data = {
        'msgtype': 'markdown',
        'markdown': {
            'content': content
        }
    }
    res = requests.post(url=f'{webhookurl}{key}', headers=headers, data=to_json(data).encode(encoding=encoding))
    res.status_code != 200 and log.error(f'发送企业微信通知失败，接口响应: {res.text}')


def image_message(key, base64: str, md5: str):
    """发送图片消息

    Args:
        base64 (str): 图片内容的base64编码，图片（base64编码前）最大不能超过2M，支持JPG,PNG格式
        md5 (str): 图片内容（base64编码前）的md5值
    """
    data = {
        'msgtype': 'image',
        'image': {
            'base64': base64,
            'md5': md5
        }
    }
    res = requests.post(url=f'{webhookurl}{key}', headers=headers, data=to_json(data).encode(encoding=encoding))
    res.status_code != 200 and log.error(f'发送企业微信通知失败，接口响应: {res.text}')


def news_message(key, articles: list):
    """发送图文消息

    Args:
        articles (list): 图文消息，一个图文消息支持1到8条图文
        title (str): 标题，不超过128个字节，超过会自动截断
        description (str): 描述，不超过512个字节，超过会自动截断
        url (str): 点击后跳转的链接
        picurl (str): 图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150
    """
    data = {
        'msgtype': 'news',
        'news': {
            'articles': articles
        }
    }
    res = requests.post(url=f'{webhookurl}{key}', headers=headers, data=to_json(data).encode(encoding=encoding))
    res.status_code != 200 and log.error(f'发送企业微信通知失败，接口响应: {res.text}')


def file_message(key, media_id: str):
    """发送文件消息

    Args:
        media_id (str): 文件id，通过文件上传接口获取
    """
    data = {
        'msgtype': 'file',
        'file': {
            'media_id': media_id
        }
    }
    res = requests.post(url=f'{webhookurl}{key}', headers=headers, data=to_json(data).encode(encoding=encoding))
    res.status_code != 200 and log.error(f'发送企业微信通知失败，接口响应: {res.text}')
