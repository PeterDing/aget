# -*- coding: utf-8 -*-

import os
import functools
import asyncio

from .request import async_request, get_content_length, request_range
from .models import File, Shower
from .utils import make_headers, exit_session
from .color import color_str


async def download(args):
# async def download(method, url,
                   # headers=None,
                   # data=None,
                   # timeout=None,
                   # config=None,
                   # chuck_size=DEFAULT_CHUCK_SIZE,
                   # concurrency=DEFAULT_CONCURRENCY):

    file_obj = File(args.out)

    method = args.method
    url = args.url
    headers = make_headers(args)
    data = args.data
    timeout = args.timeout
    chuck_size = args.chuck_size
    concurrency = args.concurrency

    content_length = await get_content_length(method, url,
                                              headers=headers,
                                              data=data,
                                              timeout=timeout)

    if file_obj.is_init():
        file_obj.record_data(content_length)
    else:
        if file_obj.info.content_length != content_length:
            print(color_str('Conflict content length:', codes=(1, 91)),
                  file_obj.info.content_length,
                  content_length)
            return None

    file_obj.info.content_length = content_length
    file_obj.create_file()

    shower = Shower(args.out,
                    content_length,
                    file_obj.info.completed_size,
                    concurrency,
                    chuck_size)

    show_task = asyncio.ensure_future(shower.show())

    ctrl_queue = asyncio.queues.Queue(maxsize=concurrency)

    part = 1
    # print(list(file_obj.undownload_chucks))
    for begin_point, end_point in file_obj.undownload_chucks:
        point = begin_point
        point_t = 0
        while point <= end_point:
            await ctrl_queue.put(None)
            point_t = min(point + chuck_size, end_point)

            task = asyncio.ensure_future(
                request_range(method, url,
                              point,
                              point_t,
                              ctrl_queue,
                              headers=headers,
                              data=data,
                              timeout=timeout))

            task.add_done_callback(
                functools.partial(save_data, file_obj,
                                  point, point_t,
                                  shower, part))

            if point == point_t:
                break

            point = min(point_t + 1, end_point)
            part += 1

    while ctrl_queue.qsize():
        await asyncio.sleep(1)

    await asyncio.sleep(1)
    file_obj.close()
    file_obj.info.remove_aget()
    exit_session()
    shower.over()
    show_task.cancel()


def save_data(file_obj, begin_point, end_point, shower, part, fut):
    data = fut.result()

    file_obj.write(data, begin_point)
    file_obj.record_data(begin_point, end_point)

    shower.append_info(part, begin_point, end_point)
