#!/usr/bin/env python3

from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation


def _coerce_int(value: object, parameter_name: str) -> object:
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError as exception:
            raise BeartypeCallHintParamViolation(
                f'divide() parameter {parameter_name}={value!r} violates type hint int, as string cannot be coerced to int.',
                culprits=(value,),
            ) from exception

    return value


@beartype
def _divide_checked(a: int, b: int) -> float:
    return a / b


def divide(a: int, b: int) -> float:
    return _divide_checked(_coerce_int(a, 'a'), _coerce_int(b, 'b'))
