from typing import List

from rich.box import ROUNDED
from rich.panel import Panel


def render_panel(
    title: str,
    res_in: str,
    vbit_in: str,
    res_out: str,
    vbit_out: str,
    audio_in: str,
    audio_out: str,
    tail_line: str,
) -> Panel:
    """
    Собирает панель с параметрами и «хвостовой» строкой (прогресс/итог)
    """
    lines: List[str] = [
        "Параметры:",
        f"  Исходник: {res_in}, vbit={vbit_in}, audio={audio_in}",
        f"  Цель:     {res_out}, vbit={vbit_out}, audio={audio_out}",
        tail_line,
    ]
    content = "\n".join(lines)
    return Panel(content, title=title, border_style="bright_blue", box=ROUNDED)


def make_bar(percent: float, width: int = 50) -> str:
    """
    Рендер прогресс-бара (зелёный), формат совместим с rich-разметкой
    """
    p = max(0.0, min(100.0, percent))
    filled = int(width * (p / 100.0))
    bar = "█" * filled + "░" * (width - filled)
    return f"[bold green][{bar}] {p:6.2f}%[/bold green]"
