import sys
from enum import Enum
from pathlib import Path
from typing import List

from loguru import logger

APP_NAME = "VideoGymnast"
APP_VERSION = "1.0"


class ModeType(Enum):
    DEV = "dev"
    PROD = "prod"


# Nuitka
if "__compiled__" in globals():
    MODE = ModeType.PROD
    BASE_DIR = Path(sys.argv[0]).resolve().parent
# PyInstaller
elif getattr(sys, "frozen", False):
    MODE = ModeType.PROD
    BASE_DIR = Path(sys.executable).resolve().parent
# Ide
else:
    MODE = ModeType.DEV
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

logger.debug(f"<Режим запуска>: {MODE}")
logger.debug(f"<Основная папка>: {BASE_DIR}")

# ---
if MODE == ModeType.PROD:
    RESOURCES_DIR = BASE_DIR / "_internal" / "resources"
    FFMPEG_BIN = RESOURCES_DIR / "ffmpeg" / "bin" / "ffmpeg"
else:
    RESOURCES_DIR = BASE_DIR / "resources"
    FFMPEG_BIN = RESOURCES_DIR / "ffmpeg" / "bin" / "ffmpeg"
    BASE_DIR = BASE_DIR / "_test"
logger.debug(f"<FFmpage - Исполняемый файл>: {FFMPEG_BIN}")

#
INPUT_PATH = BASE_DIR / "input"
OUTPUT_PATH = BASE_DIR / "output"

# Видео-расширения
VIDEO_EXTS: set[str] = {
    ".mp4", ".mkv", ".mov", ".avi", ".ts", ".m4v", ".webm", ".flv",
    ".wmv", ".mpg", ".mpeg", ".vob", ".m2ts", ".mts", ".3gp",
}

# Максимальный порог разрешения
RESOLUTION_MAX_WIDTH: int = 1920
RESOLUTION_MAX_HEIGHT: int = 1080

# Коэффициенты качества для разрешений
DEFAULT_BPP_SD: float = 0.03
DEFAULT_BPP_720P: float = 0.02
DEFAULT_BPP_1080P: float = 0.01

# FFmpeg - Общее
FFMPEG_GLOBAL_ARGS: List[str] = ["-hide_banner", "-y"]

# FFmpeg - Кодирование
FFMPEG_X264_PRESET: str = "medium"
vbv_bufsize_multiplier: float = 2.0

# FFmpeg - Аудио
DEFAULT_AUDIO_CODEC: str = "aac"
DEFAULT_AAC_BITRATE: int = 128_000

# FFmpeg - Метаданные
DEFAULT_FPS: float = 30.0
