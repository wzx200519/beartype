#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype forward-reference and type-alias expansion utilities** (i.e.,
low-level callables resolving :pep:`484`-compliant forward references *and*
recursively unwrapping :pep:`695`-compliant ``type`` statement aliases to a
concrete non-alias type hint).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep695Exception
from beartype._cave._cavefast import HintPep695TypeAlias
from beartype._data.typing.datatypingport import Hint
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_12,
)
from typing import Optional

# ....................{ EXPANDERS                          }....................
def _expand_type_alias(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    exception_cls: type = BeartypeDecorHintPep695Exception,
    exception_prefix: str = '',
    _seen: Optional[set] = None,
) -> Hint:
    '''
    Recursively expand any :pep:`695`-compliant **type alias** (i.e., object
    created by a ``type {alias_name}[{type_params}] = {alias_value}`` statement
    under Python >= 3.12) nested within the passed type hint down to a concrete
    non-alias type hint.

    This helper is the single canonical entry point for unwrapping PEP 695
    ``TypeAliasType`` objects at runtime. Specifically:

    * If ``hint`` is a :obj:`typing.TypeAliasType` (i.e., the value of a
      ``type Alias = ...`` statement), this helper returns the concrete hint
      referred to by ``hint.__value__``, recursively expanding any further
      aliases transitively referenced by that value.
    * If ``hint`` is an unparameterizable alias (e.g. ``type Alias = int``),
      the unwrapped hint is returned as is.
    * If ``hint`` is a parameterized alias (e.g. ``Alias[int]`` for some
      ``type Alias[T] = ...``), the underlying ``types.GenericAlias`` is
      returned unchanged -- its ``__origin__`` is the ``TypeAliasType`` and
      its ``__args__`` are the user-supplied type arguments; unwrapping the
      origin would throw away the arguments, so parameterized aliases are
      preserved verbatim and left to :mod:`beartype`'s existing generic
      reduction machinery.
    * If ``hint`` is *not* a PEP 695 alias, ``hint`` is returned unchanged.
    * If unwrapping encounters a cycle (e.g. ``type A = B; type B = A``), the
      loop is detected by tracking seen aliases in ``_seen`` and the original
      alias is returned instead of infinitely recursing.

    This helper is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). The underlying ``__value__`` descriptor
    of :pep:`695` aliases is itself memoized, so repeated calls are cheap;
    additionally, memoizing on the caller side would prevent the caller from
    observing redefinitions of a given alias.

    Parameters
    ----------
    hint : Hint
        Possibly-PEP-695-aliased type hint to be expanded.
    exception_cls : type, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep695Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.
    _seen : set or None, optional
        *Private* parameter used internally by this helper to track the
        ``id(...)`` of each alias already visited during the current expansion
        so as to break circular references. Callers should *never* pass this
        parameter explicitly.

    Returns
    -------
    Hint
        Concrete non-alias type hint obtained by transitively unwrapping all
        PEP 695 type aliases reachable from ``hint``, or ``hint`` unchanged if
        ``hint`` is not such an alias.

    Raises
    ------
    BeartypeDecorHintPep695Exception
        If the passed hint is a PEP 695 type alias whose ``__value__``
        descriptor raises a non-``NameError`` exception when accessed.
    '''
    assert exception_cls is not None, f'{repr(exception_cls)} None exception class.'
    assert isinstance(exception_prefix, str), f'{repr(exception_prefix)} not string.'

    # ....................{ FAST-PATH                      }....................
    # If the active Python interpreter targets Python < 3.12, PEP 695 is
    # unsupported by definition. In this case, this helper is a noop.
    if not IS_PYTHON_AT_LEAST_3_12:
        return hint
    # Else, the active Python interpreter targets Python >= 3.12 and thus
    # supports PEP 695.

    # If this hint is *NOT* a PEP 695-compliant type alias, this hint requires
    # no expansion and should be returned as is. This simultaneously rules out
    # parameterized aliases (which are "types.GenericAlias" instances rather
    # than "TypeAliasType" instances -- see below).
    if not isinstance(hint, HintPep695TypeAlias):
        return hint
    # Else, this hint is a PEP 695-compliant type alias.

    # ....................{ CYCLE-DETECTION                }....................
    # Initialize the cycle-detection set on first entry. We use "id(...)"
    # rather than the alias itself because PEP 695 alias objects are *NOT*
    # hashable in general (their hashability depends on their value) but each
    # alias object has a stable identity.
    if _seen is None:
        _seen = set()

    # "id(hint)" is a small positive integer unique to this alias object for
    # its lifetime, which is exactly what we need for cycle detection.
    hint_id = id(hint)

    if hint_id in _seen:
        # This alias has already been visited on the current expansion path,
        # implying a circular self-reference (e.g. "type A = B; type B = A").
        # Break the cycle by returning the alias itself rather than recursing
        # again. Downstream consumers (sanifiers, reducers, ...) already know
        # how to deal with (or explicitly reject) bare alias objects; we simply
        # must *not* blow the stack here.
        return hint
    # Else, this alias has *NOT* yet been visited on the current expansion
    # path. In this case, record the visit and continue.

    _seen.add(hint_id)

    # ....................{ EXPANSION                      }....................
    # Reduce this alias to the hint it aliases. Accessing "__value__" may
    # raise:
    # * "NameError" if the alias body contains one or more unresolved forward
    #   references. That is a legitimate, expected state -- the caller is
    #   responsible for resolving such references. We therefore bubble the
    #   alias itself back up, letting higher-level machinery (e.g. the
    #   "iter_hint_pep695_unsubbed_forwardrefs" iterator) deal with it.
    # * Any other exception, which we wrap in a human-readable
    #   "BeartypeDecorHintPep695Exception" prefixing the original failure.
    try:
        inner_hint: Hint = hint.__value__  # type: ignore[attr-defined]
    except NameError:
        # This alias body references one or more undefined attributes. Return
        # the alias verbatim; forward-reference resolution happens elsewhere.
        _seen.discard(hint_id)  # clean up so future expansion can retry
        return hint
    except Exception as exception:
        raise exception_cls(
            f'{exception_prefix}PEP 695 type alias '
            f'{getattr(hint, "__name__", repr(hint))} has malformed '
            f'"__value__": {exception}'
        ) from exception

    # Recursively expand any further PEP 695 aliases nested inside the value
    # returned by "__value__". This handles chains like:
    #     type A = B
    #     type B = C
    #     type C = int
    # which should collapse straight to "int".
    return _expand_type_alias(
        hint=inner_hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
        _seen=_seen,
    )
