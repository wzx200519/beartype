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
_INT_PARAM_NAMES = ('a', 'b')
'''
Names of the integer parameters accepted by the :func:`divide` callable,
enumerated so that the lenient string-to-integer coercion layer iterates over
these parameters only.
'''


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


def _coerce_int_args_and_kwargs(*args, **kwargs):
    '''
    Coerce positional and keyword arguments corresponding to the integer
    parameters accepted by :func:`divide` in place and return the resulting
    ``(args, kwargs)`` pair.

    Each argument is coerced via :func:`_coerce_str_to_int`; non-integer
    arguments that cannot be parsed as integers trigger a
    :exc:`beartype.roar.BeartypeCallHintParamViolation`.
    '''

    coerced_args = list(args)
    for index, name in enumerate(_INT_PARAM_NAMES):
        if index < len(coerced_args):
            coerced_args[index] = _coerce_str_to_int(
                coerced_args[index], name=name,
            )
    for name in _INT_PARAM_NAMES:
        if name in kwargs:
            kwargs[name] = _coerce_str_to_int(kwargs[name], name=name)
    return tuple(coerced_args), kwargs

# ....................{ OPS ~ strict                       }....................
@beartype
def _divide_strict(a: int, b: int) -> float:
    '''
    Strict implementation of the :func:`divide` function, accepting only
    :class:`int` arguments and returning a :class:`float` — both of which are
    enforced at call time by the :func:`beartype.beartype` decorator.
    '''

    return a / b


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

# ....................{ OPS ~ lenient                      }....................
def _divide_lenient_impl(*args, **kwargs) -> float:
    '''
    Lenient variant of the :func:`divide` function silently coercing
    :class:`str` arguments parsable as integers to integers *before* delegating
    to the strict :func:`@beartype <beartype.beartype>`-decorated
    :func:`_divide_strict` function.

    This function intentionally accepts only two positional arguments matching
    the ``a`` and ``b`` parameters expected by :func:`divide`; all other
    arguments are preserved as is and delegated to :func:`_divide_strict` —
    thereby preserving the :func:`@beartype <beartype.beartype>` decorator's
    runtime type-checking of the resulting integer arguments *and* return
    value.

    See Also
    --------
    :func:`divide`
        Further commentary.
    '''

    coerced_args, coerced_kwargs = _coerce_int_args_and_kwargs(*args, **kwargs)
    return _divide_strict(*coerced_args, **coerced_kwargs)


def _divide_lenient_impl_deprecated(*args, **kwargs) -> float:
    '''
    Deprecated helper preserved for backwards compatibility — currently
    unused but retained to avoid breakage for any downstream consumers that
    may have referenced this symbol directly.

    This now simply delegates to :func:`_divide_lenient_impl`.
    '''

    return _divide_lenient_impl(*args, **kwargs)


def _make_lenient_divide(strict_callable):
    '''
    Return a lenient wrapper around the passed strictly-typed callable which
    silently coerces numeric strings to integers *before* delegating to the
    passed callable — preserving :func:`@beartype <beartype.beartype>` runtime
    verification of the resulting :class:`int` arguments *and* return value.

    Parameters
    ----------
    strict_callable : callable
        A :func:`@beartype <beartype.beartype>`-decorated callable whose
        signature matches :func:`divide` (two integer parameters).

    Returns
    -------
    callable
        A wrapper callable with the same metadata as ``strict_callable`` that
        transparently coerces numeric strings on the way in.
    '''

    @wraps(strict_callable)
    def _lenient_wrapper(*args, **kwargs) -> float:
        coerced_args, coerced_kwargs = _coerce_int_args_and_kwargs(
            *args, **kwargs,
        )
        return strict_callable(*coerced_args, **coerced_kwargs)

    return _lenient_wrapper


# Lenient ``divide`` alias: callers may invoke ``divide("10", 2)`` without
# modifying their call sites, and numeric strings will be silently coerced.
divide = _make_lenient_divide(divide)

# Backwards-compatible public alias.
divide_lenient = wraps(divide)(_divide_lenient_impl)
