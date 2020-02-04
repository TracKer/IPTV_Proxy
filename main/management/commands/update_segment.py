import requests
from django.core.management import BaseCommand
from main.models import Segment


class Command(BaseCommand):
    help = 'Update segment'

    def add_arguments(self, parser):
        parser.add_argument('segment_id', nargs=1, type=int)
        pass

    def handle(self, *args, **options):
        segment_id = options['segment_id'][0]

        segment = Segment.objects.get(id=segment_id)

        self.set_status(segment, Segment.STATUS_DOWNLOADING)

        tries = 0
        max_tries = 10
        downloaded = False
        while (tries < max_tries) and (not downloaded):
            try:
                r = requests.get(segment.name_original, timeout=2)
                f = open(segment.get_file_path(), 'x')
                f.write(r.content)
                f.close()
                downloaded = True
                self.set_status(segment, Segment.STATUS_AVAILABLE)
                self.stdout.write(f'[DOWNLOAD] Segment {segment_id} - Downloaded')
            except:
                self.stdout.write(f'[DOWNLOAD] Segment {segment_id} - Failed ({tries + 1}/{max_tries})')
            tries += 1

        if not downloaded:
            self.set_status(segment, Segment.STATUS_NEW)
            self.stdout.write(f'[DOWNLOAD] Segment {segment_id} - Download failed!')

    @staticmethod
    def set_status(segment: Segment, status: int) -> None:
        segment.status = status
        segment.save()
