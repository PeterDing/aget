# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import time

from .color import color_str

from .utils import data_pack, data_unpack, sizeof_fmt, terminal_width


class File(object):

    def __init__(self, path):
        self._fd = None
        self._path = path
        self.info = Info(path)


    @property
    def fd(self):
        return self._fd


    @property
    def path(self):
        return self._path


    @property
    def undownload_chucks(self):
        return self.info.find_undownload_chucks()


    def is_init(self):
        return self.info.content_length == 0


    def create_file(self):
        path = self.path
        if os.path.exists(path):
            fd = open(path, 'rb+')
            self._fd = fd
            return fd
        else:
            _dir = os.path.dirname(path)
            if _dir and not os.path.exists(_dir):
                os.makedirs(_dir)
            fd = open(path, 'wb+')
            self._fd = fd
            return fd


    def write(self, data, seek):
        self.fd.seek(seek, 0)
        self.fd.write(data)


    def record_data(self, *datas):
        for data in datas:
            self.info.write(data)


    def close(self):
        self.fd.close()


class Info(object):

    def __init__(self, path):
        self.info_filename = path + '.aget'
        if not os.path.exists(self.info_filename):
            self.initiate_info()
        else:
            self.load_info()


    @property
    def downloaded_chucks(self):
        return self._downloaded_chucks


    @property
    def completed_size(self):
        n = 0
        for begin_point, end_point in self.downloaded_chucks:
            n += end_point - begin_point + 1
        return n


    def initiate_info(self):
        self.content_length = 0
        self._downloaded_chucks = []


    def load_info(self):
        data = open(self.info_filename, 'rb').read()
        N = len(data)
        if not data:
            self.initiate_info()
        else:
            self.content_length = data_unpack(data[:8])
            if N > 8:
                chucks = [data_unpack(data[i:i+8]) for i in range(8, N, 8)]
                self._downloaded_chucks = self.merge_chucks(chucks)
                self._dump_info(self.content_length, self.downloaded_chucks)
            else:
                self._downloaded_chucks = []


    def _dump_info(self, content_length, chucks):
        open(self.info_filename, 'wb').close()   # remove old data
        self.write(content_length)
        for begin_point, end_point in chucks:
            self.write(begin_point)
            self.write(end_point)


    def write(self, data):
        with open(self.info_filename, 'ab') as fd:
            data_byte = data_pack(data)
            fd.write(data_byte)


    def merge_chucks(self, chucks):
        if len(chucks) % 2 != 0:
            chucks = chucks[:-1]

        intervals = [chucks[i:i+2] for i in range(0, len(chucks), 2)]

        downloaded_chucks = _merge_intervals(intervals)
        return downloaded_chucks


    def find_undownload_chucks(self):
        N = self.content_length
        if not self.downloaded_chucks:
            return [[0, N-1]]
        else:
            if len(self.downloaded_chucks) == 1 \
                    and self.downloaded_chucks[0][0] == 0 \
                    and self.downloaded_chucks[0][-1] == N-1:
                return []

        chucks = [[0, 0]] + list(self.downloaded_chucks) + [[N, N]]
        undownload_chucks = _find_gaps(chucks)

        return undownload_chucks


    def remove_aget(self):
        os.remove(self.info_filename)


def _merge_intervals(intervals):
    intervals.sort()

    mt = []

    mt.append(intervals[0])
    for begin_point, end_point in intervals[1:]:
        pre_begin_point, pre_end_point = mt[-1]

        # case 1
        # ----------
        #                -----------
        if pre_end_point + 1 < begin_point:
            n_begin_point = begin_point
            n_end_point = end_point

        # case 2
        # -----------------
        #                  ----------
        #             --------
        #     ------
        else:
            n_begin_point = pre_begin_point
            n_end_point = max(pre_end_point, end_point)
            mt.pop()

        mt.append([n_begin_point, n_end_point])

    return mt


def _find_gaps(intervals):
    if len(intervals) <= 1:
        return []

    gaps = []

    for i, interval in enumerate(intervals[:-1]):
        next_interval = intervals[i+1]
        if interval[1] + 1 < next_interval[0]:
            gaps.append([interval[1] + 1, next_interval[0] - 1])
        else:
            continue

    return gaps


class Shower(object):

    TEMPLATE = ('\n {}: {{}}\n'
                ' {}: {{}} ({{}})\n').format(
                    color_str('File', codes=(1, 92)),
                    color_str('Size', codes=(1, 94))
                )


    def __init__(self, filename,
                 content_length,
                 completed_size,
                 concurrency,
                 chuck_size):

        self.filename = filename
        self.content_length = content_length
        self._completed_size = completed_size
        self._pre_size = completed_size
        self._stop = False
        self._completed_chucks = []


    @property
    def completed_size(self):
        while self._completed_chucks:
            part, begin_point, end_point = self._completed_chucks.pop()
            self._completed_size += (end_point - begin_point + 1)
        return self._completed_size


    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, value):
        self._stop = True


    async def show(self):
        total_size = sizeof_fmt(self.content_length)
        header = self.TEMPLATE.format(self.filename,
                                      total_size,
                                      self.content_length)
        print(header)

        begin_time = time.time()
        while True:
            if self.stop:
                break

            end_time = time.time()

            completed_size = self.completed_size
            download_size = completed_size - self._pre_size
            self._pre_size = completed_size

            speed = download_size // (end_time - begin_time)
            speed_str = '{: >7}/s'.format(sizeof_fmt(speed))

            width = terminal_width()
            cs = sizeof_fmt(completed_size)
            pre_width = len('{}/{} {} [] '.format(cs, total_size, speed_str))
            status = '{}/{} {}'.format(
                color_str(cs, codes=(1, 91)),
                color_str(total_size, codes=(1, 92)),
                color_str(speed_str, codes=(1,94)))
            process_line_width = width - pre_width
            p = completed_size / self.content_length
            process_line = '>' * int(p * process_line_width) \
                            + ' ' * (process_line_width - int(p * process_line_width))

            status_line = '\r{} [{}] '.format(status, process_line)
            sys.stdout.write(status_line)
            sys.stdout.flush()

            begin_time = end_time
            await asyncio.sleep(2)


    def append_info(self, part, begin_point, end_point):
        self._completed_chucks.append((part, begin_point, end_point))


    def over(self):
        print('\n' + color_str('Over.', codes=(1, 97)))
        self.stop = True
