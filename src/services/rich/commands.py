from dataclasses import dataclass
from typing import Literal

from core.commands import Command

ConsoleColors = Literal["yellow", "green", "red"]


@dataclass
class PrintToConsole(Command):
    msg: str
    color: ConsoleColors
