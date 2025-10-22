from components.utils.fs import fs_delete_files_with_suffix_before_ext, fs_create_dirs
from core.config import INPUT_PATH, OUTPUT_PATH


def app_init():
    """
    Инициализация окружение приложения
    """
    fs_create_dirs([INPUT_PATH, OUTPUT_PATH])
    fs_delete_files_with_suffix_before_ext(OUTPUT_PATH, ".tmp")
