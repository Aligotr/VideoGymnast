from components.loguru_settings import logger_settings
from components.cli_args import args_parser


def main():
    args = args_parser()
    logger_settings(args.log_level)

    # ---
    from time import sleep

    from core.config import MODE, ModeType
    from core.messagebus import MessageBus
    from services.main.entry import MainService
    from services.rich.entry import RichService
    from services.transcoder.entry import TranscoderService

    # Инициализация сервисов приложения
    bus = MessageBus()

    services = [
        RichService(bus),
        TranscoderService(bus),
        MainService(bus),
    ]

    # Запрос подтверждения о закрытии приложения
    if MODE == ModeType.PROD:
        sleep(1)
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()
