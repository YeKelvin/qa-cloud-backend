#!/usr/bin python3
# @File    : http_client.py
# @Time    : 2023-09-06 10:26:45
# @Author  : Kelvin.Ye
import httpx

from loguru import logger

from app.tools.exceptions import ServiceError


def _request(method, url, **kwargs) -> httpx.Response:
    kwargs['timeout'] = 10
    try:
        res = httpx.request(method, url, **kwargs)
        if not res.is_success:
            logger.info(f'url:[ {method} {url} ] {res.status_code} 请求失败')
            raise ServiceError('{res.status_code} 第三方请求失败')
        return res
    except httpx.ReadTimeout as e:
        logger.info(f'url:[ {method} {url} ] 请求超时')
        raise ServiceError('第三方请求超时') from e


def post(url, json):
    return _request(
        method='POST',
        url=url,
        json=json,
        headers={'content-type': 'application/json'}
    ).json()
