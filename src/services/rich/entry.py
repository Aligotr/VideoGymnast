from typing import Optional

from rich.box import ROUNDED
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from core.messagebus import AbstractMessageBus
from services.main.events import (OnAppException, OnFileDataProcessed,
                                  OnGetFileToTranscode, OnMsgNoFilesToTranscode)
from services.transcoder.events import (OnTranscodingCompleted,
                                        OnTranscodingProgressEvent)

from .commands import PrintToConsole
from .rich_elements import make_bar, render_panel


class RichService:

    def __init__(self, bus: AbstractMessageBus) -> None:

        self.bus = bus
        self.bus.subscribe_command(PrintToConsole, self.print_to_console)
        self.bus.subscribe_event(OnMsgNoFilesToTranscode, self.print_to_console)
        self.bus.subscribe_event(OnGetFileToTranscode, self.on_get_file_to_transcode)
        self.bus.subscribe_event(OnAppException, self.on_app_exception)
        self.bus.subscribe_event(OnFileDataProcessed, self.on_transcode_prepare)
        self.bus.subscribe_event(
            OnTranscodingProgressEvent, self.on_transcoding_progress_event
        )
        self.bus.subscribe_event(OnTranscodingCompleted, self.on_transcoding_completed)

        # Переменные для переиспользования при повторных вызовах событий относящихся к одним и тем же файлам
        self.console = Console()
        self._live: Optional[Live] = None
        self.transcoding_progress_event_data = {}

    def print_to_console(self, cmd: PrintToConsole):
        """
        Печать сообщения указанным цветом
        """
        self.console.print(f"[bold {cmd.color}]{cmd.msg}[/bold {cmd.color}]")

    def on_msg_no_files_to_transcode(self, e: OnMsgNoFilesToTranscode):
        self.print_to_console(PrintToConsole(e.msg, e.color))

    def on_app_exception(self, e: OnAppException):
        self.console.print(f"[bold red]{e.msg}[/bold red]")

    def on_get_file_to_transcode(self, e: OnGetFileToTranscode) -> None:
        """
        Печать списка файлов в красной рамке
        """
        lines = [f"- {p.name}" for p in e.files]
        lines.append(f"Итого: {len(e.files)} файл(ов)")
        content = "\n".join(lines)
        panel = Panel(content, title="Файлы:", border_style="bright_red", box=ROUNDED)
        self.console.print(panel)

    def on_transcode_prepare(self, e: OnFileDataProcessed):
        """
        Событие: Перекодирование видео
        Подготовка переменных для отображения в рамке
        """
        self.transcoding_progress_event_data = {
            "title": e.input_file.name,
            "res_in": f"{e.src_media_info.src_width}x{e.src_media_info.src_height}",
            "vbit_in": str(e.src_media_info.src_video_bitrate_avg),
            "res_out": f"{e.output_media_params.width}x{e.output_media_params.height}",
            "vbit_out": str(e.output_media_params.video_bitrate_avg),
            "audio_in": str(e.src_media_info.src_audio_codec),
            "audio_out": e.output_media_params.audio_codec,
        }

    def on_transcoding_progress_event(self, e: OnTranscodingProgressEvent):
        """
        Событие: Перекодирование видео
        Обновление строк во время выполнения процесса
        """
        panel = render_panel(
            tail_line=f"Прогресс: {make_bar(e.progress_value)}",
            **self.transcoding_progress_event_data,
        )

        if self._live is None:
            self._live = Live(panel, console=self.console, refresh_per_second=1)
            self._live.start()
        else:
            self._live.update(panel)

    def on_transcoding_completed(self, e: OnTranscodingCompleted):
        """
        Событие: Перекодирование видео
        Завершение процесса, выход из "Live" и очистка переменных
        """
        if self._live:
            if e.ok:
                tail_line = f"[bold green][ ГОТОВО ][/bold green] {e.msg}"
            else:
                tail_line = f"[bold yellow][ ВНИМАНИЕ ][/bold yellow] {e.msg}"

            self._live.update(
                render_panel(
                    tail_line=tail_line,
                    **self.transcoding_progress_event_data,
                )
            )
            self._live.stop()
            self._live = None
            self.transcoding_progress_event_data = {}
