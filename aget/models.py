# -*- coding: utf-8 -*-

import os
import sys
import asyncio

from .color import color_str

from .utils import data_pack, data_unpack, sizeof_fmt, terminal_width


class File(object):

    def __init__(self, path):
        if os.path.exists(path):
            fd = open(path, 'rb+')
        else:
            fd = self.create_file(path)

        self._fd = fd
        self.info = Info(path)


    @property
    def fd(self):
        return self._fd

    @property
    def undownload_chucks(self):
        return self.info.find_undownload_chucks()


    def is_init(self):
        return self.info.content_length == 0


    def create_file(self, path):
        _dir = os.path.dirname(path)
        if _dir and not os.path.exists(_dir):
            os.makedirs(_dir)

        fd = open(path, 'wb+')
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
        internals = [chucks[i:i+2] for i in range(0, len(chucks), 2)]
        internals.sort()

        downloaded_chucks = []
        downloaded_chucks.append(internals[0])
        for begin_point, end_point in internals[1:]:
            pre_begin_point, pre_end_point = downloaded_chucks[-1]

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
                downloaded_chucks.pop()

            downloaded_chucks.append([n_begin_point, n_end_point])

        return downloaded_chucks


    def find_undownload_chucks(self):
        N = self.content_length - 1
        if not self.downloaded_chucks:
            return [[0, N]]
        else:
            if len(self.downloaded_chucks) == 1 \
                    and self.downloaded_chucks[0][0] == 0 \
                    and self.downloaded_chucks[0][-1] == N:
                return []

        chucks = [[0, 0]] + list(self.downloaded_chucks) + [[N, N]]
        undownload_chucks = []
        for i, chuck1 in enumerate(chucks[:-1]):
            chuck2 = chucks[i+1]
            if chuck1[1] == chuck2[0]:
                continue
            else:
                undownload_chucks.append((chuck1[1] + 1, chuck2[0] - 1))
        return undownload_chucks


    def remove_aget(self):
        os.remove(self.info_filename)


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

        while True:
            if self.stop:
                break

            width = terminal_width()
            cs = sizeof_fmt(self.completed_size)
            pre_width = len('{}/{} []'.format(cs, total_size))
            status = '{}/{}'.format(color_str(cs, codes=(1, 91)),
                                    color_str(total_size, codes=(1, 92)))
            process_line_width = width - pre_width
            p = self.completed_size / self.content_length
            process_line = '>' * int(p * process_line_width) \
                           + ' ' * (process_line_width - int(p * process_line_width))

            status_line = '\r{} [{}]'.format(status, process_line)
            sys.stdout.write(status_line)
            sys.stdout.flush()

            await asyncio.sleep(2)


    def append_info(self, part, begin_point, end_point):
        self._completed_chucks.append((part, begin_point, end_point))


    def over(self):
        print('\n' + color_str('Over.', codes=(1, 97)))
        self.stop = True
