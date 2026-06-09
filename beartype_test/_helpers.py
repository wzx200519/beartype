from typing import cast

from beartype import beartype
from beartype.roar import BeartypeException


@beartype
def validate_and_convert(
    items: list[int | str],
    factor: float = 1.0,
) -> list[float]:
    return [
        float((item if isinstance(item, int) else int(item)) * factor)
        for item in items
    ]


def test_validate_and_convert_inline() -> None:
    assert validate_and_convert([1, '2', 3], 2.5) == [2.5, 5.0, 7.5]

    exception = None

    try:
        validate_and_convert(cast(list[int | str], [1, 2.5]))
    except BeartypeException as exception_caught:
        exception = exception_caught

    assert exception is not None
    assert isinstance(exception, BeartypeException)
