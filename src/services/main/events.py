from dataclasses import dataclass
from pathlib import Path

from core.events import Event
from services.rich.commands import ConsoleColors
from services.main.models import OutputMediaParams, SrcMediaInfo


@dataclass
class OnMsgNoFilesToTranscode(Event):
    msg: str
    color: ConsoleColors


@dataclass
class OnGetFileToTranscode(Event):
    files: list[Path]


@dataclass
class OnFileDataProcessed(Event):
    input_file: Path
    src_media_info: SrcMediaInfo
    output_media_params: OutputMediaParams


@dataclass
class OnAppException(Event):
    msg: str
