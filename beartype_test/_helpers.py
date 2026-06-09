#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **test helper callables** (i.e., ad-hoc utilities called by
*both* unit and functional tests exercising arbitrary beartype-specific
concerns).
'''

# ....................{ IMPORTS                            }....................
from beartype import beartype

# ....................{ HELPERS                            }....................
@beartype
def validate_and_convert(
    items: list[int | str],
    factor: float = 1.0,
) -> list[float]:
    '''
    Validate that the passed list contains *only* integers *or* strings and
    return a new list of floats produced by coercing each element to an
    :class:`int` and multiplying by the passed ``factor``.

    Parameters
    ----------
    items : list[int | str]
        Input list whose elements are either integers or string representations
        of integers.
    factor : float, optional
        Multiplicative factor applied to each element after coercion.

    Returns
    -------
    list[float]
        New list of floats whose ``i``-th element is
        ``int(items[i]) * factor``.

    Raises
    ------
    BeartypeCallHintParamViolation
        If the caller passes a list containing any element that is *not* an
        :class:`int` or :class:`str` (e.g., a :class:`float`).
    ValueError
        If any string element cannot be coerced to an :class:`int`.
    '''

    return [int(item) * factor for item in items]


def test_validate_and_convert() -> None:
    '''
    Inline test exercising :func:`.validate_and_convert`, notably including
    the case in which :func:`beartype.beartype` raises a
    :class:`BeartypeException` on receiving an invalidly typed list.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeException
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert mixed int/str lists are correctly converted.
    assert validate_and_convert([1, 2, 3]) == [1.0, 2.0, 3.0]
    assert validate_and_convert(['1', '2', '3']) == [1.0, 2.0, 3.0]
    assert validate_and_convert([10, '20', 30], factor=2.0) == [20.0, 40.0, 60.0]

    # ....................{ FAIL                           }....................
    # Assert @beartype raises a BeartypeException when the input list
    # contains a value violating the list[int | str] type hint (e.g., a
    # float).
    with raises(BeartypeException):
        validate_and_convert([1, '2', 3.0])

    # Assert Python itself raises ValueError on uncoercible strings (this
    # exercises the function body rather than the @beartype decorator).
    with raises(ValueError):
        validate_and_convert(['not-an-int'])
