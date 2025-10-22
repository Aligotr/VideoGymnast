from core.config import (DEFAULT_AAC_BITRATE, DEFAULT_AUDIO_CODEC,
                         DEFAULT_BPP_720P, DEFAULT_BPP_1080P, DEFAULT_BPP_SD,
                         RESOLUTION_MAX_HEIGHT, RESOLUTION_MAX_WIDTH)
from services.main.models import OutputMediaParams


def build_media_params(
    src_width: int,
    src_height: int,
    src_fps: float,
    src_video_bitrate_avg: int,
    src_audio_codec: str,
    src_audio_bitrate: int,
) -> OutputMediaParams:
    width, height = choose_target_resolution(src_width, src_height)
    video_avg_bps = choose_target_video_avg_bitrate(
        width, height, src_fps, src_video_bitrate_avg
    )
    video_maxrate_bps = video_avg_bps
    video_bufsize_bps = video_avg_bps * 2
    src_audio_codec, src_audio_bitrate = choose_audio_params(
        src_audio_codec, src_audio_bitrate
    )

    return OutputMediaParams(
        width=width,
        height=height,
        video_bitrate_avg=video_avg_bps,
        video_bitrate_bufsize=video_bufsize_bps,
        video_bitrate_max=video_maxrate_bps,
        audio_codec=src_audio_codec,
        audio_bitrate_bps=src_audio_bitrate,
    )


def choose_audio_params(audio_codec: str, audio_bitrate_bps: int) -> tuple[str, int]:
    if not audio_codec or audio_codec == "":
        return "copy", 0
    if audio_codec == DEFAULT_AUDIO_CODEC and audio_bitrate_bps < DEFAULT_AAC_BITRATE:
        return "copy", 0
    return DEFAULT_AUDIO_CODEC, DEFAULT_AAC_BITRATE


def choose_target_resolution(w, h) -> tuple[int, int]:
    def _to_even(value: int) -> int:
        """
        Делает значение чётным (уменьшая на 1 при необходимости).
        """
        return value if value % 2 == 0 else value - 1

    def _scale_to_fit(w: int, h: int, max_w: int, max_h: int) -> tuple[int, int]:
        """
        Пропорционально вписывает (w,h) в рамку (max_w,max_h) и приводит к чётным значениям.
        Не увеличивает изображение, только уменьшает.
        """
        if w <= max_w and h <= max_h:
            return _to_even(w), _to_even(h)
        k = min(max_w / w, max_h / h)
        tw = _to_even(int(w * k))
        th = _to_even(int(h * k))
        return max(2, tw), max(2, th)

    # Выбор масштабирования в зависимости от соотношения сторон
    if w > h:
        return _scale_to_fit(w, h, RESOLUTION_MAX_WIDTH, RESOLUTION_MAX_HEIGHT)
    return _scale_to_fit(w, h, RESOLUTION_MAX_HEIGHT, RESOLUTION_MAX_WIDTH)


def choose_target_video_avg_bitrate(
    w: int, h: int, fps: float, video_avg_bitrate: int
) -> int:

    def recommended_bitrate() -> int:
        def _default_bpp_for() -> float:
            # Рекомендация битрейта в зависимости от количества пикселей
            pixels = w * h
            if pixels <= 640 * 480:
                return DEFAULT_BPP_SD
            if pixels <= 1280 * 720:
                return DEFAULT_BPP_720P
            return DEFAULT_BPP_1080P

        default_bpp = _default_bpp_for()
        rec_video_avg_bitrate = w * h * fps * default_bpp
        return int(rec_video_avg_bitrate)

    rec_bps = recommended_bitrate()
    if video_avg_bitrate > 0:
        return int(min(rec_bps, video_avg_bitrate))
    return int(rec_bps)
