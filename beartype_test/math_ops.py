#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Mathematical operation test utilities.**

This test-only submodule declares simple callables exercising core
:mod:`beartype` functionality — including runtime type-checking of both
parameters *and* returns via the :func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation
from functools import wraps

# ....................{ HELPERS                            }....................
def _coerce_str_to_int(value, *, name: str):
    '''
    Attempt to coerce the passed value to an :class:`int`.

    Specifically, if the passed value is already an :class:`int`, this function
    returns that value as is. If that value is a :class:`str` parsable as an
    :class:`int`, this function returns the resulting :class:`int`. In all
    other cases, this function raises a
    :exc:`beartype.roar.BeartypeCallHintParamViolation` — the same exception
    class that the :func:`beartype.beartype` decorator itself raises on
    parameter type violations — so that *all* type-related failures from the
    wrapped callable are uniformly reportable via :mod:`beartype` exceptions.

    Parameters
    ----------
    value : object
        Arbitrary object to be coerced.
    name : str
        Human-readable name of the parameter corresponding to this object,
        embedded in the exception message for debugging purposes.

    Returns
    -------
    int
        :class:`int` coerced from this object.

    Raises
    ------
    beartype.roar.BeartypeCallHintParamViolation
        If this object is neither an :class:`int` *nor* a :class:`str`
        parsable as an :class:`int`.
    '''

    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except (TypeError, ValueError) as exception:
            raise BeartypeCallHintParamViolation(
                f'Parameter "{name}" not int-like: '
                f'{type(value).__name__} {repr(value)}'
            ) from exception
    raise BeartypeCallHintParamViolation(
        f'Parameter "{name}" not int-like: '
        f'{type(value).__name__} {repr(value)}'
    )

# ....................{ OPS                                }....................
@beartype
def divide(a: int, b: int) -> float:
    '''
    Quotient of the first passed integer divided by the second passed integer
    as a floating-point number.

    This function is intentionally decorated by the
    :func:`beartype.beartype` decorator to verify that both parameters are
    strictly :class:`int` instances at call time *and* that the value returned
    at call time is a :class:`float` instance.

    Caveats
    -------
    Since this function is :func:`@beartype <beartype.beartype>`-decorated,
    passing non-:class:`int` arguments (e.g., numeric strings like ``"10"``)
    raises :mod:`beartype` exceptions. Callers requiring string-to-integer
    coercion should instead call the
    :func:`beartype_test.math_ops.divide_lenient` alias instead.

    Parameters
    ----------
    a : int
        First integer to be divided.
    b : int
        Second integer to divide by.

    Returns
    -------
    float
        Quotient of this division.
    '''

    return a / b


def _divide_lenient(*args, **kwargs) -> float:
    '''
    Lenient variant of the :func:`divide` function silently coercing
    :class:`str` arguments parsable as integers to integers *before* delegating
    to the strict :func:`@beartype <beartype.beartype>`-decorated
    :func:`divide` function.

    This function intentionally accepts only two positional arguments matching
    the ``a`` and ``b`` parameters expected by :func:`divide`; all other
    arguments are preserved as is and delegated to :func:`divide` — thereby
    preserving the :func:`@beartype <beartype.beartype>` decorator's runtime
    type-checking of the resulting integer arguments *and* return value.

    See Also
    --------
    :func:`divide`
        Further commentary.
    '''

    coerced_args = list(args)
    if coerced_args:
        coerced_args[0] = _coerce_str_to_int(coerced_args[0], name='a')
    if len(coerced_args) > 1:
        coerced_args[1] = _coerce_str_to_int(coerced_args[1], name='b')
    if 'a' in kwargs:
        kwargs['a'] = _coerce_str_to_int(kwargs['a'], name='a')
    if 'b' in kwargs:
        kwargs['b'] = _coerce_str_to_int(kwargs['b'], name='b')
    return divide(*coerced_args, **kwargs)


divide_lenient = wraps(divide)(_divide_lenient)
'''
Lenient variant of the :func:`divide` function silently coercing numeric
strings (e.g., ``"10"``) to integers *before* delegating to the strict
:func:`@beartype <beartype.beartype>`-decorated :func:`divide` function.
'''
