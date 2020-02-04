import sys
from binascii import crc32
import m3u8
from datetime import datetime
from typing import List, Optional
from django.core.management.base import OutputWrapper
from django.utils.timezone import get_default_timezone
from m3u8 import M3U8, Playlist, Segment as M3U8_Segment
from main.models import Source, Segment


class SourceProcessor:
    def __init__(self, stdout: OutputWrapper, url: Optional[str] = None, source: Optional[Source] = None) -> None:
        super().__init__()

        self.stdout = stdout
        self.__url = url
        self.__source = source
        self.__display_name: str = ''

        if (self.__url is None) and (self.__source is None):
            raise Exception('Both url and source can not be None')

        if self.__url is None:
            self.__url = self.__source.url
            self.__display_name = crc32(self.__url)
        elif self.__source is None:
            self.__display_name = crc32(self.__url)
            try:
                # Try to find in DB
                self.__source = Source.objects.get(url=self.__url)
            except Source.DoesNotExist:
                # Get from external source
                self.__source = Source()
                self.update_source(force=True)

    def update_source(self, force: bool = False) -> None:
        if force or self.__source.is_data_outdated():
            self.__source = self.__get_from_external_source(self.__source)

    def __get_from_external_source(self, source: Optional[Source] = None) -> Source:
        m3u8_obj = self.__download_m3u8(self.__url)
        name = Source.generate_name(self.__url)

        tz = get_default_timezone()
        now = datetime.now(tz)

        if source is None:
            source = Source()
        source.name = name
        source.url = self.__url
        source.last_sequence = m3u8_obj.media_sequence
        source.target_duration = round(m3u8_obj.target_duration)
        source.segments_per_file = len(m3u8_obj.segments)
        source.requested_by_server = now

        if self.__source.last_sequence >= source.last_sequence:
            self.stdout.write(f'[DOWNLOAD] Downloaded source {self.__display_name} has outdated sequence')
            raise Exception()

        source.save()

        self.__process_segments(m3u8_obj.segments)

        return source

    def __download_m3u8(self, url: str) -> M3U8:
        tries = 0
        max_tries = 10
        downloaded = False
        m3u8_obj = None
        while (tries < max_tries) and (not downloaded):
            try:
                m3u8_obj = m3u8.load(url, 3)
                downloaded = True
                self.stdout.write(f'[DOWNLOAD] Source {self.__display_name} - Downloaded')
            except:
                e_type, e_value, traceback = sys.exc_info()[0]
                self.stdout.write(f'[DOWNLOAD] Source {self.__display_name} - Failed ({tries}/{max_tries})')
            tries += 1

        if not downloaded:
            self.stdout.write(f'[DOWNLOAD] Source {self.__display_name} - Download failed!')
            raise Exception()

        if m3u8_obj.is_variant:
            playlist = self.__get_biggest_bitrate(m3u8_obj.playlists)
            return self.__download_m3u8(playlist.absolute_uri)

        return m3u8_obj

    @staticmethod
    def __get_biggest_bitrate(playlists: List[Playlist]) -> Playlist:
        result = playlists[0]
        bandwidth = playlists[0].stream_info.bandwidth
        for playlist in playlists:
            if bandwidth < playlist.stream_info.bandwidth:
                result = playlist
                bandwidth = playlist.stream_info.bandwidth
        return result

    def __process_segments(self, segments_list: List[M3U8_Segment]):
        segments_m3u8 = self.__filter_out_existent_segments(segments_list)

        # Add new segments to DB
        for segment_m3u8 in segments_m3u8:
            segment = Segment()
            segment.source = self.__source
            segment.duration = segment_m3u8.duration
            segment.name = f'{self.__source.id}-{Segment.generate_name(segment_m3u8.absolute_uri)}'
            segment.name_original = segment_m3u8.absolute_uri
            segment.status = Segment.STATUS_NEW
            segment.save()

    @staticmethod
    def __filter_out_existent_segments(segments_list: List[M3U8_Segment]) -> List[M3U8_Segment]:
        segments_m3u8 = {segment_m3u8.absolute_uri: segment_m3u8 for segment_m3u8 in segments_list}
        segments_db = Segment.objects.get(name_original__in=segments_m3u8.keys())

        # Remove segments that are already in DB
        for segment_db in segments_db:
            if segment_db.name_original in segments_m3u8.keys():
                del segments_m3u8[segment_db.name_original]

        return list(segments_m3u8.values())
