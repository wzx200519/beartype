#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype forward type hint utilities.

This private subpackage is *not* intended for importation by downstream callers.
'''

from beartype.roar import (
    BeartypeCallHintForwardRefException,
    BeartypeDecorHintPep695Exception,
)
from beartype._cave._cavefast import HintPep695TypeAlias
from beartype._data.typing.datatyping import TypeException
from beartype._data.typing.datatypingport import Hint


def _expand_type_alias(
    hint: Hint,
    exception_cls: TypeException = BeartypeCallHintForwardRefException,
    exception_prefix: str = '',
) -> Hint:
    if not isinstance(hint, HintPep695TypeAlias):
        return hint

    from beartype._util.hint.pep.proposal.pep695 import (
        get_hint_pep695_unsubbed_alias)

    try:
        return get_hint_pep695_unsubbed_alias(
            hint=hint,
            exception_prefix=exception_prefix,
        )
    except BeartypeDecorHintPep695Exception as exception:
        raise exception_cls(str(exception)) from exception
