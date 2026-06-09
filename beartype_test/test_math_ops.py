#!/usr/bin/env python3

from beartype.roar import BeartypeCallHintParamViolation
from beartype_test.math_ops import divide
from pytest import raises


def test_divide_accepts_ints() -> None:
    assert divide(10, 2) == 5.0


def test_divide_coerces_numeric_strings() -> None:
    assert divide("10", 2) == 5.0
    assert divide(10, "2") == 5.0


def test_divide_raises_beartype_for_non_numeric_strings() -> None:
    with raises(BeartypeCallHintParamViolation):
        divide("ten", 2)



def test_divide_preserves_beartype_validation_for_non_int_inputs() -> None:
    with raises(BeartypeCallHintParamViolation):
        divide(10.5, 2)
