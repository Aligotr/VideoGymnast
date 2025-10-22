from pathlib import Path

from pymediainfo import MediaInfo

from core.config import DEFAULT_FPS
from services.main.models import SrcMediaInfo

from components.utils.formatters import to_float_or_raise, to_int, to_int_or_raise


def get_media_info(path: Path) -> SrcMediaInfo:
    mi = MediaInfo.parse(path)
    vtrack = next((t for t in mi.tracks if t.track_type == "Video"), None)
    atrack = next((t for t in mi.tracks if t.track_type == "Audio"), None)
    if not (vtrack and atrack):
        raise ValueError(f"Ошибка чтения исходного файла: {path}")

    # Фпс
    fps = getattr(vtrack, "frame_rate", None)
    if not fps:
        fps = float(DEFAULT_FPS)

    # Битрейт
    video_bitrate_bps = getattr(vtrack, "bit_rate", None)

    # Аудио
    audio_codec = (
        getattr(atrack, "format", None) or getattr(atrack, "codec_id", None) or ""
    ).lower()
    audio_bitrate_bps = getattr(atrack, "bit_rate", None)

    # Разрешение
    width = getattr(vtrack, "width", None)
    height = getattr(vtrack, "height", None)

    return SrcMediaInfo(
        src_width=to_int_or_raise(width),
        src_height=to_int_or_raise(height),
        src_fps=to_float_or_raise(fps),
        src_video_bitrate_avg=to_int(video_bitrate_bps),
        src_audio_codec=audio_codec,
        src_audio_bitrate=to_int(audio_bitrate_bps),
    )
