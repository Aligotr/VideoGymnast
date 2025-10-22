""" https://gitflic.ru/project/max40in/max40in/file/?file=architecture&branch=master """

import abc
import inspect
import queue
import threading
from typing import Any, Callable, Union

from loguru import logger

from core.commands import Command
from core.events import Event

Message = Union[Command, Event]


class AbstractMessageBus(abc.ABC):
    event_handlers: dict[type[Event], list[Callable]] = {}
    command_handlers: dict[type[Command], Callable] = {}

    def add_dependency(self, name: str, dep: Any) -> None: ...
    def update_dependencies(self, deps: dict[str, Any]) -> None: ...
    def subscribe_event(self, event: type[Event], callback: Callable) -> None: ...
    def subscribe_command(self, command: type[Command], callback: Callable) -> None: ...
    def publish(self, message: Message) -> Any | None: ...


class MessageBus(AbstractMessageBus):
    event_handlers: dict[type[Event], list[Callable]] = {}
    command_handlers: dict[type[Command], Callable] = {}

    def __init__(self):
        self._event_queue = queue.Queue()
        self.dependencies: dict[str, Any] = {}
        threading.Thread(target=self._dispatcher, daemon=True).start()

    # --- Публичный API (в логическом порядке использования) ---

    def add_dependency(self, name: str, dep: Any) -> None:
        """Добавляет или обновляет одну зависимость по имени."""
        if not isinstance(name, str):
            raise TypeError("Имя зависимости должно быть строкой")
        self.dependencies[name] = dep
        logger.trace("Добавлена зависимость: {0} = {1}", name, dep)

    def update_dependencies(self, deps: dict[str, Any]) -> None:
        """Добавляет или обновляет несколько зависимостей."""
        if not isinstance(deps, dict):
            raise TypeError("Зависимости должны быть переданы как dict[str, Any]")
        self.dependencies.update(deps)
        logger.trace("Обновлены зависимости: {0}", list(deps.keys()))

    def subscribe_event(self, event: type[Event], callback: Callable):
        wrapped = self._wrap(callback)
        if event in self.event_handlers:
            self.event_handlers[event].append(wrapped)
        else:
            logger.debug("event={0} не найден. Добавляем в словарь событий.", event)
            self.event_handlers[event] = [wrapped]
        logger.trace(
            "event={0} += {1} len({2})={3}.",
            event,
            _get_callback_info(callback),
            event.__qualname__,
            len(self.event_handlers[event]),
        )

    def subscribe_command(self, command: type[Command], callback: Callable):
        """Подписывает функцию `callback` на команды типа `command_type`."""
        # Предотвращение перезаписи обработчика
        if command in self.command_handlers:
            raise ValueError(
                f"Команде {command} уже назначен обработчик {_get_callback_info(callback)}."
            )
        wrapped = self._wrap(callback)
        self.command_handlers[command] = wrapped
        logger.trace("command={0} += {1}.", command, _get_callback_info(callback))

    def publish(self, message: Message) -> Any | None:
        if isinstance(message, Event):
            self.handle_event(message)
            return None
        elif isinstance(message, Command):
            return self.handle_command(message)
        else:
            raise ValueError(f"{message} не Event или Command")

    def handle_event(self, event: Event) -> None:
        self._event_queue.put(event)

    def handle_command(self, command: Command) -> Any | None:
        try:
            handler = self.command_handlers[type(command)]
            return handler(command)
        except Exception as e:
            logger.exception(e)
            raise

    # --- Внутренние методы (protected) ---

    def _wrap(self, callback: Callable) -> Callable[[Message], None]:
        sig = inspect.signature(callback)

        # Запрещаем *args и **kwargs
        for param in sig.parameters.values():
            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                raise ValueError(
                    f"Обработчик {callback} не должен использовать *args или **kwargs. "
                    f"Найден параметр: {param.name} (kind={param.kind.name})"
                )

        # Пропускаем первый параметр (event/command)
        params = list(sig.parameters.items())
        dep_names = [name for i, (name, param) in enumerate(params) if i > 0]
        missing = [n for n in dep_names if n not in self.dependencies]
        if missing:
            raise LookupError(
                f"Отсутствуют зависимости для обработчика {callback}: {missing}"
            )

        def _handler(message: Message) -> None:
            deps = {n: self.dependencies[n] for n in dep_names}
            return callback(message, **deps)

        _handler.__qualname__ = getattr(callback, "__qualname__", str(callback))
        _handler.__module__ = getattr(callback, "__module__", None)  # type: ignore
        return _handler

    def _dispatcher(self):
        while True:
            event = self._event_queue.get()
            for h in self.event_handlers.get(type(event), []):
                try:
                    h(event)
                except (ValueError, TypeError) as e:
                    logger.exception("event={0}. e={1}", event, e)
                    continue


def _get_callback_info(callback: Callable[[Any], None]) -> str:
    try:
        sig = inspect.signature(callback)
        params = str(sig)
    except ValueError:
        params = "(...)"
    if hasattr(callback, "__qualname__"):
        qualname = callback.__qualname__
        module = getattr(callback, "__module__", None)
        if module:
            return f"{module}.{qualname}{params}"
        return f"{qualname}{params}"
    if hasattr(callback, "__class__"):
        cls = callback.__class__
        module = getattr(cls, "__module__", None)
        name = getattr(cls, "__name__", str(cls))
        if module:
            return f"{module}.{name}{params}"
        return f"{name}{params}"
    return f"{callback}{params}"


bus = MessageBus()
