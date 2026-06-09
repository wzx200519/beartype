#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **type hint helper utilities** (i.e., low-level callables exercising
:func:`beartype.beartype` runtime type-checking against PEP-compliant type
hints including ``list[int | str]``).
'''

# ....................{ IMPORTS                            }....................
from beartype import beartype
from beartype.roar import BeartypeException

# ....................{ FUNCTIONS                          }....................
@beartype
def validate_and_convert(items: list[int | str], factor: float = 1.0) -> list[float]:
    '''
    Validate and convert the passed list of integer and/or string items into a
    list of floating-point numbers, each multiplied by the passed factor.

    This function validates the passed ``items`` list to contain *only*
    integers and/or strings at runtime via the :func:`beartype.beartype`
    decorator. String items are first converted to integers and then multiplied
    by ``factor``; integer items are multiplied by ``factor`` directly.

    Parameters
    ----------
    items : list[int | str]
        List of integer and/or string items to be validated and converted.
    factor : float
        Floating-point factor by which to multiply each converted item.
        Defaults to ``1.0``.

    Returns
    -------
    list[float]
        List of floating-point numbers derived from converting and multiplying
        the passed items.

    Raises
    ------
    BeartypeException
        If any item in ``items`` is neither an :class:`int` nor a :class:`str`
        (e.g., a :class:`float`).
    '''
    return [int(item) * factor for item in items]


# ....................{ TESTS                              }....................
def test_validate_and_convert_raises_on_float() -> None:
    '''
    Test that the :func:`validate_and_convert` function raises a
    :class:`BeartypeException` when passed a list containing floating-point
    numbers, which violate the ``list[int | str]`` type hint enforced at
    runtime by the :func:`beartype.beartype` decorator.
    '''
    from pytest import raises

    with raises(BeartypeException):
        validate_and_convert([1, 2.5, 3])

    with raises(BeartypeException):
        validate_and_convert([1.0])

    with raises(BeartypeException):
        validate_and_convert(["1", 3.14, "5"])
