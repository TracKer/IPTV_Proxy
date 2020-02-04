from django.core.management import BaseCommand, CommandError
from main.core.SourceProcessor import SourceProcessor
from main.models import Source


class Command(BaseCommand):
    help = 'Update source'

    def add_arguments(self, parser):
        parser.add_argument('source_id', nargs=1, type=int)
        pass

    def handle(self, *args, **options):
        source_id = options['source_id'][0]

        source = Source.objects.get(id=source_id)

        processor = SourceProcessor(self.stdout, source=source)
        processor.update_source()
