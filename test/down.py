
import sys
import os
import asyncio
import mugen
import argparse

# Defines that should never be changed
OneK = 1024
OneM = OneK * OneK
OneG = OneM * OneK
OneT = OneG * OneK
OneP = OneT * OneK
OneE = OneP * OneK

DEFAULT_CHUCK_SIZE = 1 * OneM
DEFAULT_CONCURRENCY = 10


async def request(method, url, **kwargs):
    while True:
        try:
            resp = await mugen.request(method, url, **kwargs)
            return resp
        except Exception:
            await asyncio.sleep(1)


async def request_range(port, method, url, start, end, fd, queue, **kwargs):
    headers = {'Range': 'bytes={}-{}'.format(start, end)}
    headers.update(kwargs.get('headers') or {})
    kwargs['headers'] = headers

    resp = await request(method, url, **kwargs)
    fd.seek(start, 0)
    fd.write(resp.content)

    print('over', port, start, end)
    await queue.get()


async def get_content_length(method, url, **kwargs):
    if kwargs.get('headers'):
        headers = {'Range': 'bytes=0-1'}
        headers.update(kwargs.get('headers') or {})
    else:
        headers = {'Range': 'bytes=0-1'}

    kwargs['headers'] = headers

    resp = await request(method, url, **kwargs)
    # resp = await mugen.head(url)
    return int(resp.headers['Content-Range'].split('/')[-1])
    # print(resp.headers['Content-Length'])
    # return int(resp.headers['Content-Length'])


async def download(method, url,
                   headers=None,
                   data=None,
                   timeout=None,
                   chuck_size=DEFAULT_CHUCK_SIZE,
                   concurrency=DEFAULT_CONCURRENCY):

    content_length = await get_content_length(method, url,
                                              headers=headers,
                                              data=data,
                                              timeout=timeout)
    print(content_length)
    fd = open('out', 'wb+')

    queue = asyncio.queues.Queue(maxsize=concurrency)

    i = 0
    ii = -1
    port = 1
    while i != ii:
        await queue.put(None)
        ii = min(i + chuck_size, content_length - 1)
        asyncio.ensure_future(request_range(port, method, url, i, ii, fd, queue,
                                            headers=headers,
                                            data=data,
                                            timeout=timeout))
        i = min(ii + 1, content_length - 1)
        port += 1

    while queue.qsize():
        print(queue.qsize())
        await asyncio.sleep(1)

    fd.close()

    print('# over')


def handle_args(argv):
    p = argparse.ArgumentParser(description='')

    p.add_argument('xxx', type=str, help='命令对象.')
    p.add_argument('-H', '--header', action='append',
                   default=[], help='header')
    p.add_argument('-X', '--method', action='store',
                   default='GET', type=str, help='')
    p.add_argument('-s', '--concurrency', action='store',
                   default=DEFAULT_CONCURRENCY, type=int, help='')
    p.add_argument('-k', '--chuck_size', action='store',
                   default=str(DEFAULT_CHUCK_SIZE), type=str, help='')
    p.add_argument('-d', '--data', action='store',
                   default=None, help='')
    p.add_argument('-t', '--timeout', action='store',
                   default=10 * 60, type=int, help='')

    args = p.parse_args(argv)

    return args


def make_headers(args):
    headers = {}
    for header in args.header:
        k, v = header.split(': ', 1)
        headers[k] = v
    return headers


def get_chuck_size(args):
    size = args.chuck_size
    if size.isdigit():
        return int(size)
    elif size.endswith('K'):
        s = int(size[:-1]) * OneK
        return s
    elif size.endswith('M'):
        s = int(size[:-1]) * OneM
        return s
    else:
        return DEFAULT_CHUCK_SIZE


def main(args):
    url = args.xxx
    # url = 'https://raw.githubusercontent.com/racaljk/hosts/master/hosts'

    method = args.method
    headers = make_headers(args)
    data = args.data
    timeout = args.timeout
    chuck_size = get_chuck_size(args)
    concurrency = args.concurrency
    if data:
        method = 'POST'

    try:
        loop = asyncio.get_event_loop()
        # loop.run_forever()
        loop.run_until_complete(download(method, url,
                                         headers=headers,
                                         data=data,
                                         timeout=timeout,
                                         chuck_size=chuck_size,
                                         concurrency=concurrency))
        s = mugen.session()
        s.close()
    except:
        pass


if __name__ == '__main__':
    argv = sys.argv[1:]
    args = handle_args(argv)
    main(args)
