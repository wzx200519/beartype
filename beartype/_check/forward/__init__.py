#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference** subpackage.

This subpackage is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._cave._cavefast import HintPep695TypeAlias
from beartype._data.typing.datatypingport import Hint
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12

# ....................{ EXPANDERS                          }....................
def _expand_type_alias(
    hint: Hint,
    exception_prefix: str = '',
) -> Hint:
    '''
    Recursively expand the passed **PEP 695 type alias** (i.e., object created
    by a ``type X = ...`` statement) to its underlying **base type hint** (i.e.,
    non-TypeAliasType type hint) that this alias transitively resolves to.

    This expander safely handles **chained aliases** (i.e., aliases whose values
    are themselves aliases) as well as **self-referencing aliases** by detecting
    and preventing infinite loops via identity-based cycle detection.

    Parameters
    ----------
    hint : Hint
        Type hint to be possibly expanded. If this hint is *not* a PEP
        695-compliant type alias, it is returned as is.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Hint
        Either:

        * If this hint is a PEP 695 type alias, the non-alias base type hint
          that this alias transitively resolves to.
        * Else, this hint as is.

    Raises
    ------
    BeartypeDecorHintPep695Exception
        If a self-referencing cycle is detected among chained type aliases.

    See Also
    --------
    :func:`beartype._util.hint.pep.proposal.pep695.get_hint_pep695_unsubbed_alias`
        Lower-level getter that this function wraps with additional cycle
        detection safety guarantees.
    '''

    if not IS_PYTHON_AT_LEAST_3_12:
        return hint

    hint_expanded: Hint = hint
    visited_ids: set[int] = set()

    while isinstance(hint_expanded, HintPep695TypeAlias):
        hint_id = id(hint_expanded)

        if hint_id in visited_ids:
            from beartype.roar import BeartypeDecorHintPep695Exception
            raise BeartypeDecorHintPep695Exception(
                f'{exception_prefix}PEP 695 type alias cycle detected: '
                f'{repr(hint_expanded)} transitively references itself. '
                f'Self-referencing type aliases are unsupported by '
                f'@beartype.'
            )

        visited_ids.add(hint_id)

        hint_expanded = hint_expanded.__value__

    return hint_expanded