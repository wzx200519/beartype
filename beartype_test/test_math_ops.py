#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Mathematical operation test suite.**

This test-only submodule tests the
:mod:`beartype_test.math_ops` submodule.
'''

# ....................{ IMPORTS                            }....................
from beartype_test.math_ops import (
    divide,
    divide_lenient,
)
from beartype.roar import BeartypeCallHintParamViolation
from pytest import raises

# ....................{ TESTS ~ strict                     }....................
def test_divide_strict_int() -> None:
    '''
    Test that the :func:`beartype_test.math_ops.divide` function accepts
    integer arguments.
    '''

    assert divide(10, 2) == 5.0


def test_divide_strict_str_rejected() -> None:
    '''
    Test that the :func:`beartype_test.math_ops.divide` function rejects
    string arguments by raising a :mod:`beartype` exception.
    '''

    with raises(BeartypeCallHintParamViolation):
        divide("10", 2)


def test_divide_strict_float_rejected() -> None:
    '''
    Test that the :func:`beartype_test.math_ops.divide` function rejects
    floating-point arguments by raising a :mod:`beartype` exception.
    '''

    with raises(BeartypeCallHintParamViolation):
        divide(10.0, 2)

# ....................{ TESTS ~ lenient                     }....................
def test_divide_lenient_int() -> None:
    '''
    Test that the :func:`beartype_test.math_ops.divide_lenient` function
    still accepts plain integer arguments.
    '''

    assert divide_lenient(10, 2) == 5.0


def test_divide_lenient_str_int() -> None:
    '''
    Test that the :func:`beartype_test.math_ops.divide_lenient` function
    accepts numeric string arguments and coerces them to integers.
    '''

    assert divide_lenient("10", 2) == 5.0
    assert divide_lenient(10, "2") == 5.0
    assert divide_lenient("10", "2") == 5.0


def test_divide_lenient_negative_str() -> None:
    '''
    Test that the :func:`beartype_test.math_ops.divide_lenient` function
    accepts negative numeric string arguments.
    '''

    assert divide_lenient("-7", "2") == -3.5


def test_divide_lenient_uncoercible_str_rejected() -> None:
    '''
    Test that the :func:`beartype_test.math_ops.divide_lenient` function
    rejects uncoercible strings by raising a :mod:`beartype` exception.
    '''

    with raises(BeartypeCallHintParamViolation):
        divide_lenient("not_a_number", 2)


def test_divide_lenient_other_type_rejected() -> None:
    '''
    Test that the :func:`beartype_test.math_ops.divide_lenient` function
    rejects non-string non-integer types by raising a :mod:`beartype` exception.
    '''

    with raises(BeartypeCallHintParamViolation):
        divide_lenient(None, 2)


def test_divide_lenient_return_type() -> None:
    '''
    Test that the :func:`beartype_test.math_ops.divide_lenient` function
    preserves the strict ``float`` return-type guarantee of the underlying
    :func:`beartype_test.math_ops.divide` function.
    '''

    result = divide_lenient("10", 2)
    assert isinstance(result, float)
