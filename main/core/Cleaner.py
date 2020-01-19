from main.models import Segment, Source


class Cleaner:
    @classmethod
    def do_cleanup(cls) -> None:
        cls.cleanup_segments()
        cls.cleanup_sources()

    @staticmethod
    def cleanup_segments() -> None:
        segments = Segment.objects.all()
        for segment in segments:
            if segment.is_outdated():
                segment.delete()

    @staticmethod
    def cleanup_sources() -> None:
        sources = Source.objects.all()
        for source in sources:
            if source.is_source_outdated():
                for segment in source.segments:
                    segment.delete()
                source.delete()
