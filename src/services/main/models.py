from dataclasses import dataclass


@dataclass
class SrcMediaInfo:
    src_width: int
    src_height: int
    src_fps: float
    src_video_bitrate_avg: int
    src_audio_codec: str
    src_audio_bitrate: int


@dataclass
class OutputMediaParams:
    width: int
    height: int
    video_bitrate_avg: int
    video_bitrate_max: int
    video_bitrate_bufsize: int
    audio_codec: str
    audio_bitrate_bps: int
