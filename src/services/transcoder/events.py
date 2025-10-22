from dataclasses import dataclass

from core.events import Event


@dataclass
class OnTranscodingProgressEvent(Event):
    progress_value: float


@dataclass
class OnTranscodingCompleted(Event):
    ok: bool
    msg: str
