def to_int(v) -> int:
    """
    Преобразовать значение в целое число или вернуть "0"
    """
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def to_int_or_raise(v) -> int:
    """
    Преобразовать значение в целое число или сообщить об ошибке
    """
    try:
        return int(v)
    except (TypeError, ValueError) as exc:
        raise ValueError("Недопустимое значение") from exc


def to_float_or_raise(v) -> float:
    """
    Преобразовать значение в число с точкой или сообщить об ошибке
    """
    try:
        return float(v)
    except (TypeError, ValueError) as exc:
        raise ValueError("Недопустимое значение") from exc
