#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : wecom.py
# @Time    : 2022-05-08 15:13:18
# @Author  : Kelvin.Ye
import requests

from app.tools.logger import get_logger
from app.utils.json_util import to_json


log = get_logger(__name__)


webhookurl = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='
headers = {'content-type': 'application/json'}
encoding = 'utf-8'


def send_text_message(robotkey: str, content: str, mentioned_list: list = None, mentioned_mobile_list: list = None):
    """发送文本消息

    Args:
        robotkey (str): 机器人唯一标识
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
    res = requests.post(url=f'{webhookurl}{robotkey}', headers=headers, data=to_json(data).encode(encoding=encoding))
    res.status_code != 200 and log.error(f'发送企业微信通知失败，接口响应: {res.text}')


def send_markdown_message(robotkey: str, content: str):
    """发送markdown消息

    Args:
        robotkey (str): 机器人唯一标识
        content (str): markdown内容，最长不超过4096个字节，必须是utf8编码
    """
    data = {
        'msgtype': 'markdown',
        'markdown': {
            'content': content
        }
    }
    res = requests.post(url=f'{webhookurl}{robotkey}', headers=headers, data=to_json(data).encode(encoding=encoding))
    res.status_code != 200 and log.error(f'发送企业微信通知失败，接口响应: {res.text}')


def send_image_message(robotkey: str, base64: str, md5: str):
    """发送图片消息

    Args:
        robotkey (str): 机器人唯一标识
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
    res = requests.post(url=f'{webhookurl}{robotkey}', headers=headers, data=to_json(data).encode(encoding=encoding))
    res.status_code != 200 and log.error(f'发送企业微信通知失败，接口响应: {res.text}')


def send_news_message(robotkey: str, articles: list):
    """发送图文消息

    Args:
        robotkey (str): 机器人唯一标识
        articles (list): 图文消息，一个图文消息支持1到8条图文
            - title (str): 标题，不超过128个字节，超过会自动截断
            - description (str): 描述，不超过512个字节，超过会自动截断
            - url (str): 点击后跳转的链接
            - picurl (str): 图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150
    """
    data = {
        'msgtype': 'news',
        'news': {
            'articles': articles
        }
    }
    res = requests.post(url=f'{webhookurl}{robotkey}', headers=headers, data=to_json(data).encode(encoding=encoding))
    res.status_code != 200 and log.error(f'发送企业微信通知失败，接口响应: {res.text}')


def send_file_message(robotkey: str, media_id: str):
    """发送文件消息

    Args:
        robotkey (str): 机器人唯一标识
        media_id (str): 文件id，通过文件上传接口获取
    """
    data = {
        'msgtype': 'file',
        'file': {
            'media_id': media_id
        }
    }
    res = requests.post(url=f'{webhookurl}{robotkey}', headers=headers, data=to_json(data).encode(encoding=encoding))
    res.status_code != 200 and log.error(f'发送企业微信通知失败，接口响应: {res.text}')


def send_textcard_message(robotkey: str, card: dict):
    """
    {
        'template_card': {
            'card_type': 'text_notice',
            'source': {
                'icon_url': '来源图片的url',
                'desc': ''来源图片的描述',
                'desc_color': 来源文字的颜色，目前支持：0(默认) 灰色，1 黑色，2 红色，3 绿色
            },
            'main_title': {
                'title': '一级标题',
                'desc': '标题辅助信息'
            },
            'emphasis_content': {
                'title': '关键数据样式的数据内容',
                'desc': '关键数据样式的数据描述内容'
            },
            'quote_area': {
                'type': 引用文献区域点击事件，0或不填代表没有点击事件，1 代表跳转url，2 代表跳转小程序,
                'url': '引用文献样式的点击跳转的url',
                'title': '引用标题',
                'quote_text': '引用文案'
            },
            'sub_title_text': '二级普通文本',
            'horizontal_content_list': [
                {
                    'type': 链接类型，0或不填代表是普通文本，1 代表跳转url，2 代表下载附件，3 代表@员工,
                    'keyname': '二级标题',
                    'value': '二级文本',
                    'url': '链接跳转的url',
                    'media_id': '附件的media_id',
                    'userid': '被@的成员的userid',
                }
            ],
            'jump_list': [
                {
                    'type': 跳转链接类型，0或不填代表不是链接，1 代表跳转url，2 代表跳转小程序
                    'title': '跳转链接样式的文案内容',
                    'url': '跳转链接的url'
                }
            ],
            'card_action': {
                'type': 1,
                'url': '跳转事件的url'
            }
        }
    }
    """
    data = {
        'msgtype': 'template_card',
        'template_card': card
    }
    res = requests.post(url=f'{webhookurl}{robotkey}', headers=headers, data=to_json(data).encode(encoding=encoding))
    res.status_code != 200 and log.error(f'发送企业微信通知失败，接口响应: {res.text}')
