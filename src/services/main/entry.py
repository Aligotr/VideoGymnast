from dataclasses import asdict
from pathlib import Path

from components.app_init import app_init
from components.build_media_params import build_media_params
from components.get_media_info import get_media_info
from core.config import INPUT_PATH, OUTPUT_PATH, VIDEO_EXTS
from core.messagebus import AbstractMessageBus
from services.transcoder.commands import OnTranscoderRun

from .events import OnAppException, OnFileDataProcessed, OnGetFileToTranscode, OnMsgNoFilesToTranscode


class MainService:

    def __init__(self, bus: AbstractMessageBus) -> None:
        self.bus = bus
        self.run()

    def run(self):
        app_init()
        self.run_pipeline()

    def run_pipeline(self) -> None:
        files = scan_input(VIDEO_EXTS, INPUT_PATH)
        todo = [f for f in files if not (OUTPUT_PATH / f.name).exists()]

        if not todo:
            self.bus.publish(
                OnMsgNoFilesToTranscode("Нет файлов для конвертации", "yellow")
            )
            return

        self.bus.publish(OnGetFileToTranscode(todo))

        for input_file in todo:
            try:
                src_media_info = get_media_info(input_file)
                output_media_params = build_media_params(**asdict(src_media_info))
                self.bus.publish(
                    OnFileDataProcessed(input_file, src_media_info, output_media_params)
                )
                self.bus.publish(OnTranscoderRun(input_file, output_media_params))
            except (ValueError, TypeError) as e:
                self.bus.publish(OnAppException(str(e)))


def scan_input(exts: set[str], input_dir: Path) -> list[Path]:
    """
    Возвращает отфильтрованный список файлов с допустимыми расширениями из exts
    """
    return [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
