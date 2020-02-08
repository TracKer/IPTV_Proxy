import os
from subprocess import Popen
from time import sleep
from typing import List

from django.core.management import BaseCommand

from IPTV_Proxy.settings import BASE_DIR
from main.core import Cleaner
from main.models import Source, Segment


class Command(BaseCommand):
    help = 'Main cycle'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.processes: List[Popen] = []

    def add_arguments(self, parser):
        # parser.add_argument('in_file', nargs=1, type=str)
        # parser.add_argument('out_file', nargs=1, type=str)
        pass

    def handle(self, *args, **options):
        self.stdout.write('Starting cycle')

        manage_py_path = os.path.join(BASE_DIR, 'manage.py')

        dots_in_line: int = 0
        while True:
            Cleaner.do_cleanup()

            sources = self.find_sources_for_data_update()
            for source in sources:
                process = Popen(['python3', manage_py_path, 'update_source', source.id])
                process.custom_tag = ('update_source', source.id)
                self.processes.append(process)

            segments = self.find_segments_for_download()
            for segment in segments:
                pass

            self.terminate_finished_processes()
            sleep(1)
            self.stdout.write('.', ending='')

            dots_in_line += 1
            if dots_in_line >= 20:
                dots_in_line = 0
                self.stdout.write('\n', ending='')

    @staticmethod
    def find_sources_for_data_update() -> List[Source]:
        sources = Source.objects.all()
        result = []
        for source in sources:
            if source.is_data_outdated():
                result.append(source)
        return result

    @staticmethod
    def find_segments_for_download() -> List[Segment]:
        segments = Segment.objects.filter(status=Segment.STATUS_NEW).order_by('id')
        result = []
        for segment in segments:
            if segment.is_outdated():
                result.append(segment)
        return result

    def terminate_finished_processes(self):
        for process in self.processes:
            poll = process.poll()
            if poll is None:
                continue

            operation, params = process.custom_tag

            if poll == 0:
                self.stdout.write(f'Process {operation}-{params} - SUCCESS')
            else:
                self.stdout.write(f'Process {operation}-{params} - FAILED')

            process.terminate()
            self.processes.remove(process)
