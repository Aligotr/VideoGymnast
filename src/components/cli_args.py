from argparse import ArgumentParser

LOGURU_LEVELS = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]


def args_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--log-level",
        "-l",
        default="WARNING",
        type=str.upper,
        choices=LOGURU_LEVELS,
        help="Уровень логирования для консоли (по умолчанию \"WARNING\")",
    )
    return parser.parse_args()
