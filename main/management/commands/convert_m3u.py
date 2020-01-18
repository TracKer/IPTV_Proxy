import os
from typing import List, IO

from django.core.management import BaseCommand
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from main.vendor.M3uParser import M3uParser

import logging


class Command(BaseCommand):
    help = 'Parse offices from DOU'

    in_file = r'C:\Tmp\iptv\in.m3u'
    out_file = r'C:\Tmp\iptv\out.m3u'

    def add_arguments(self, parser):
        # parser.add_argument('in_file', nargs=1, type=str)
        # parser.add_argument('out_file', nargs=1, type=str)
        pass

    def handle(self, *args, **options):
        log = logging.StreamHandler()
        log.setLevel(logging.DEBUG)

        parser = M3uParser(log)
        parser.readM3u(self.in_file)
        lines: List[dict] = parser.getList()

        for line in lines:
            url = line['link']
            if self.is_modification_needed(url):
                line['link'] = self.generate_url(url)

            # print(line['link'])

        self.save(lines)

    @staticmethod
    def is_modification_needed(url: str) -> bool:
        prefixes = (
            'http://50.7.220.130:8081/',
            'http://50.7.144.75:8081/',
        )

        for prefix in prefixes:
            found = url.startswith(prefix)
            if not found:
                continue
            return found

        return False

    @classmethod
    def get_out_file(cls) -> IO:
        if os.path.exists(cls.out_file):
            os.remove(cls.out_file)

        return open(cls.out_file, 'x')

    def generate_url(self, url: str) -> str:
        return 'http://127.0.0.1:8000/m3u8/' + urlsafe_base64_encode(force_bytes(url))

    def save(self, lines: List[dict]) -> None:
        file = self.get_out_file()

        file.write('#EXTM3U\n')

        for line in lines:
            rec = line.copy()

            link = rec['link']
            title = rec['title']
            del rec['titleFile']
            del rec['link']
            del rec['title']

            file.write('#EXTINF:-1')
            for key in rec.keys():
                value = rec[key]
                file.write(f' {key}="{value}"')
            file.write(f',{title}\n')
            file.write(f'{link}\n')
