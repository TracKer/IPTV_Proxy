import hashlib
from typing import List

import m3u8
from m3u8 import M3U8, PlaylistList, Playlist

from main.models import Source


class SourceProcessor:
    def __init__(self, url: str) -> None:
        super().__init__()
        self.url = url

    def get_source(self) -> Source:
        source = Source.objects.get(url=self.url)
        if source is None:
            source = self.get_source_from_external()
            source.save()

        return source

    def get_source_from_external(self) -> Source:
        m3u8_obj = self.download_m3u8(self.url)
        name = Source.generate_name(self.url)

        source = Source()
        source.name = name
        source.url = self.url
        source.last_sequence = m3u8_obj.media_sequence
        source.target_duration = round(m3u8_obj.target_duration)
        source.segments_per_file = len(m3u8_obj.segments)

        return source

    def download_m3u8(self, url: str) -> M3U8:
        m3u8_obj = m3u8.load(url, 30)
        if m3u8_obj.is_variant:
            playlist = self.get_biggest_bitrate(m3u8_obj.playlists)
            return self.download_m3u8(playlist.absolute_uri)

        return m3u8_obj

    @staticmethod
    def get_biggest_bitrate(playlists: List[Playlist]) -> Playlist:
        result = playlists[0]
        bandwidth = playlists[0].stream_info.bandwidth
        for playlist in playlists:
            if bandwidth < playlist.stream_info.bandwidth:
                result = playlist
                bandwidth = playlist.stream_info.bandwidth
        return result


