from dataclasses import dataclass
from pathlib import Path

from core.commands import Command
from services.main.models import OutputMediaParams


@dataclass
class OnTranscoderRun(Command):
    input_file: Path
    output_media_params: OutputMediaParams
