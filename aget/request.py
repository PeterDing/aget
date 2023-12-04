# -*- coding: utf-8 -*-

import asyncio
import httpx

from .common import OK_STATUSES
from .exceptions import ContentLengthError, HttpNotOk


async def async_request(method, url, ok=False, **kwargs):
    while True:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.request(method, url, **kwargs)
                if ok:
                    if resp.status_code in OK_STATUSES:
                        return resp
                    else:
                        raise HttpNotOk(resp.status_code)
                else:
                    return resp
        except Exception:
            await asyncio.sleep(0.1)


async def request_range(method, url, start, end, ctrl_queue, **kwargs):
    headers = dict(kwargs.get("headers", {}))
    headers["Range"] = "bytes={}-{}".format(start, end)
    kwargs["headers"] = headers

    resp = await async_request(method, url, ok=True, **kwargs)
    await ctrl_queue.get()
    return resp.content


async def get_content_length(method, url, **kwargs):
    # get size from range
    headers = dict(kwargs["headers"] or {})
    headers["Range"] = "bytes=0-1"
    kwargs["headers"] = headers
    resp = await async_request(method, url, ok=True, **kwargs)
    if resp.headers.get("Content-Range"):
        size = int(resp.headers["Content-Range"].split("/")[-1])
        return size

    raise ContentLengthError("Server does not support partially downloaded")
