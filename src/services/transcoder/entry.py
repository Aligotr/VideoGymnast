from pathlib import Path
from shutil import copy2
from typing import List, Tuple

import humanfriendly as hf
from ffmpeg_progress_yield import FfmpegProgress

from core.config import (FFMPEG_BIN, FFMPEG_GLOBAL_ARGS, FFMPEG_X264_PRESET,
                         OUTPUT_PATH)
from core.messagebus import AbstractMessageBus
from services.main.models import OutputMediaParams
from services.transcoder.events import (OnTranscodingCompleted,
                                        OnTranscodingProgressEvent)

from .commands import OnTranscoderRun


class TranscoderService:
    """
    Перекодирование видео
    - Получение названий временных и конечных файлов
    - Формирование строки параметров
    - Запуск процесса
    - Проверка размера исходного файла,
      если итог больше, то замена на исходный,
      иначе убрать временные суффиксы из названия
    """

    def __init__(self, bus: AbstractMessageBus) -> None:
        self.bus = bus
        self.bus.subscribe_command(OnTranscoderRun, self.run)

    def run(
        self,
        cmd: OnTranscoderRun,
    ):
        output_temp, output_final = build_output_paths(cmd.input_file.name)
        try:
            cmd_str = compile_cmd(cmd.input_file, output_temp, cmd.output_media_params)

            ff = FfmpegProgress(cmd_str)
            for progress in ff.run_command_with_progress():
                self.bus.publish(OnTranscodingProgressEvent(progress_value=progress))

            ok, msg = finalize_output(cmd.input_file, output_temp, output_final)

            self.bus.publish(OnTranscodingCompleted(ok, msg))
        except (ValueError, TypeError) as e:
            output_temp.unlink()
            self.bus.publish(OnTranscodingCompleted(False, str(e)))


def compile_cmd(
    input_file: Path,
    output_file: Path,
    output_media_params: OutputMediaParams,
) -> List[str]:
    is_mp4 = output_file.suffix.lower() == ".mp4"
    w, h = output_media_params.width, output_media_params.height
    vb = str(output_media_params.video_bitrate_avg)
    maxrate = str(output_media_params.video_bitrate_max)
    bufsize = str(output_media_params.video_bitrate_bufsize)

    base = [
        str(FFMPEG_BIN),
        "-i", str(input_file),
        "-c:v", "libx264",
        "-preset", FFMPEG_X264_PRESET,
        "-vf", f"scale={w}:{h}:flags=lanczos",
        "-b:v", vb,
        "-maxrate", maxrate,
        "-bufsize", bufsize,
        "-c:a", output_media_params.audio_codec,
    ]

    mp4_opts = ["-pix_fmt", "yuv420p", "-movflags", "+faststart"] if is_mp4 else []
    audio_bitrate = (
        ["-b:a", str(output_media_params.audio_bitrate_bps)] if output_media_params.audio_bitrate_bps > 0 else []
    )

    return [*base, *mp4_opts, *audio_bitrate, *FFMPEG_GLOBAL_ARGS, str(output_file)]


def finalize_output(input_file: Path, output_temp: Path, output_final: Path) -> tuple[bool, str]:
    if not output_temp.exists():
        raise FileNotFoundError(f"Временный файл не найден: {output_temp}")

    src_size = input_file.stat().st_size
    out_size = output_temp.stat().st_size

    if out_size > src_size:
        output_temp.unlink()
        copy2(input_file, output_final)
        return False, "Итоговый файл больше исходного, заменён исходником"

    if output_final.exists():
        output_final.unlink()
    output_temp.replace(output_final)
    out_size_fmt = hf.format_size(out_size, binary=False)

    return True, f"{output_final.name} ({out_size_fmt})"


def build_output_paths(input_file_name: str) -> Tuple[Path, Path]:
    """
    Строит пути: временный (name + ".tmp" + ext) и финальный (name + ext).
    """
    final_output = OUTPUT_PATH / input_file_name
    temp_output = final_output.with_name(final_output.stem + ".tmp" + final_output.suffix)
    return temp_output, final_output
