# -*- coding: utf-8 -*-

import asyncio
import mugen

from .common import OK_STATUSES
from .exceptions import ContentLengthError


async def async_request(method, url, **kwargs):
    while True:
        try:
            resp = await mugen.request(method, url, **kwargs)
            if resp.status_code in OK_STATUSES:
                return resp
        except Exception:
            await asyncio.sleep(1)


async def request_range(method, url, start, end, ctrl_queue, **kwargs):
    headers = {'Range': 'bytes={}-{}'.format(start, end)}
    headers.update(kwargs.get('headers') or {})
    kwargs['headers'] = headers

    resp = await async_request(method, url, **kwargs)
    await ctrl_queue.get()
    return resp.content


async def get_content_length(method, url, **kwargs):
    # get size from HEAD
    if method.lower() == 'get':
        _method = 'HEAD'

        headers = kwargs.get('headers')
        kwargs['headers'] = headers
        resp = await async_request(_method, url, **kwargs)
        if resp.headers.get('Content-Length'):
            size = int(resp.headers.get('Content-Length'))
            return size

    # get size from range
    headers = kwargs['headers'] or {}
    headers['Range'] = {'bytes=0-1'}
    kwargs['headers'] = headers
    resp = await async_request(method, url, **kwargs)
    if resp.headers.get('Content-Range'):
        size = int(resp.headers['Content-Range'].split('/')[-1])
        return size

    raise ContentLengthError('Server does not support partially downloaded')
