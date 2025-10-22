from pathlib import Path
from typing import Iterable, List, Union


def fs_create_dirs(dirs) -> None:
    """
    Создать папки из переданного списка, если они не существуют
    """
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def fs_delete_files_with_suffix_before_ext(
    path: Union[str, Path],
    suffix: str,
    recursive: bool = True,
    dry_run: bool = False
) -> List[Path]:
    """
    Удаляет файлы, в имени которых присутствует заданный суффикс, перед финальным расширением.
    Файлы, у которых этот суффикс является финальным расширением (например, 'report.tmp'),
    не трогаются.

    Параметры:
      - root: корневая папка для поиска (str или Path).
      - suffix: искомый суффикс. Можно указывать с точкой или без:
                '.tmp' или 'tmp' — эквивалентно.
      - recursive: искать рекурсивно (True) или только в указанной папке (False).
      - dry_run: если True — ничего не удаляется, только возвращается список кандидатов.

    Возвращает:
      Список путей удалённых (или намеченных к удалению при dry_run=True) файлов.

    Примеры:
      - Удалит: photo.tmp.jpg, archive.tmp.tar.gz, video.tmp.mp4
      - Не удалит: notes.tmp, file.TMP (только расширение .tmp), data.tmp
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    # Нормализуем суффикс: добавим точку при необходимости и приведём к нижнему регистру
    norm_suffix = suffix.strip()
    if not norm_suffix:
        raise ValueError("suffix must be a non-empty string")
    if not norm_suffix.startswith("."):
        norm_suffix = "." + norm_suffix
    norm_suffix = norm_suffix.lower()

    # Генерация списка файлов
    it: Iterable[Path] = path.rglob("*") if recursive else path.glob("*")

    def has_target_suffix(p: Path) -> bool:
        # Ищем заданный суффикс среди всех суффиксов, кроме последнего
        suffixes = [s.lower() for s in p.suffixes]
        return len(suffixes) >= 2 and norm_suffix in suffixes[:-1]

    candidates: List[Path] = []
    for p in it:
        # Учитываем только обычные файлы (в т.ч. симлинки на файлы)
        if p.is_file() and has_target_suffix(p):
            candidates.append(p)

    deleted: List[Path] = []
    for p in candidates:
        try:
            if not dry_run:
                p.unlink()
            deleted.append(p)
        except (ValueError, TypeError) as e:
            # Можно логировать или собрать ошибки отдельно
            print(f"Не удалось удалить {p}: {e}")

    return deleted
