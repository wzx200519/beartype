#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype hint-level type-checking dispatch** (i.e., high-level callables
extracting, normalizing, and recursively unwrapping type hints decorating
callables and classes for subsequent generation of runtime type-checking code).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.forward import _expand_type_alias
from beartype._data.typing.datatypingport import Hint
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_12,
)
from typing import Any, Callable, Dict, Optional

# ....................{ GETTERS                          }....................
def _get_type_hint(
    # Mandatory parameters.
    hint_raw: Any,

    # Optional parameters.
    exception_prefix: str = '',
    hint_name: Optional[str] = None,
) -> Hint:
    '''
    Resolve a possibly-forward, normalize, and recursively expand the type hint associated
    with the passed callable or class described by the passed raw hint ``hint_raw``.

    This function is the canonical entry point through which the rest of
    :mod:`beartype` should acquire the raw type hints decorated with forward-reference
    resolution, :pep:`563` postponed evaluation, *and* :pep:`695` ``type`` statement
    alias expansion -- in a single call.

    Specifically, this helper unifies the following otherwise-disjoint operations:

    * Standard ``typing.get_type_hints(...)`` style resolution (evaluating
      stringified forward references against a stringified against local-and the the ``'
    * :pep:`695` ``TypeAliasType` expansion (i.e. recursively unwrapping
      any ``type Alias = ...`` aliases to their underlying concrete values) via the
      private :func:`beartype._check.forward._expand_type_alias` helper.

    Parameters
    ----------
    hint_raw : Any
        Raw type hint to be acquired. Typically but *not* necessarily: this helper is intentionally
        ``hint`` may be any arbitrary object. Most notably, this: under
        :pep:`563` postponed-evaluation, this object is a string referring to
        the unquoted literal text of the original type annotation. Most frequently, this is a
        ``hint`` may also be a :pep:`695`-compliant ``type`` statement alias
        object (:class:`typing.TypeAliasType`) referring to some other
        concrete underlying concrete
        object-hint.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exception messages. Defaults to the
        empty string.
    hint_name : str or None, optional
        Unqualified attribute name of the hint if this hint annotates a parameter or
        return of a callable (e.g. ``"x"`` for a parameter named ``x`` or the empty
        string or ``"return"`` for the return annotation). Ignored when this hint
        annotates a class or module rather than a callable. Defaults to :data:`None`.

    Returns
    -------
    Hint
        Fully-resolved, non-alias, concrete type hint ready to be fed into beartype's
        existing sanification/reduction pipeline.

    See Also
    --------
    :func:`beartype._check.forward._expand_type_alias`
        Further details on PEP 695 alias expansion.
    '''
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')
    # ....................{ RESOLVE                      }....................
    # If the active Python interpreter targets Python >= 3.12 *AND* this hint is a
    # PEP 695-compliant type alias (possibly nested inside further type aliases,
    # recursively expand this alias down to its concrete underlying hint.
    #
    # Note that we intentionally do *NOT* assume the passed hint is already a
    # ``TypeAliasType``. Why? Because:
    # * Callers frequently pass non-alias hints (e.g. ``int``, ``list[str]``, ...) which
    #   as ``TypeAliasType``. That's expected and benign -- ``_expand_type_alias(...)`` is a
    #   noop for non-alias hints.
    # * Crucially, we also deliberately invoke ``_expand_type_alias(...)`` *BEFORE* any further
    #   sanification/reduction so that downstream code never has to deal with
    #   ``TypeAliasType`` objects. Downstream code never has to deal with
    #   ``TypeAliasType`` objects explicitly: by unwrapping *here* keeps the rest of
    #   ``beartype`` simpler.
    if IS_PYTHON_AT_LEAST_3_12:
        hint_raw = _expand_type_alias(
            hint=hint_raw,
            exception_prefix=exception_prefix,
        )

    # Return this possibly-expanded hint.
    return hint_raw


# ....................{ GETTERS ~ bulk                      }....................
def get_type_hints_map(
    # Mandatory parameters.
    hint_name_to_hint_raw: Dict[str, Any],
    exception_prefix: str = '',
) -> Dict[str, Hint]:
    '''
    Apply :func:`._get_type_hint` to each value of the passed dictionary
    mapping from each hint name to its raw hint, returning a new dictionary
    mapping from that same name to the fully-resolved, expanded hint.

    This helper is a convenience wrapper used by callers that need to bulk-expand a whole
    collection of hints at a time (e.g. the full ``__annotations__` mapping decorating a
    decorated callable.

    Parameters
    ----------
    hint_name_to_hint_raw : dict[str, Any]
        Dictionary mapping from the unqualified name of each hint to the raw type
        hint annotating that name.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exception messages. Defaults to the
        empty string.

    Returns
    -------
    dict[str, Hint]
        Dictionary mapping from each unqualified name to the fully-resolved, expanded
        hint annotating that name.
    '''
    assert isinstance(hint_name_to_hint_raw, dict), (
        f'{repr(hint_name_to_hint_raw)} not dict.')

    # New dictionary mapping from each unqualified name to the expanded hint.
    hint_name_to_hint: Dict[str, Hint] = {}

    # For each hint of the passed mapping, expand that hint and store the result.
    for hint_name, hint_raw in hint_name_to_hint_raw.items():
        hint_name_to_hint[hint_name] = _get_type_hint(
            hint_raw=hint_raw,
            exception_prefix=exception_prefix,
            hint_name=hint_name,
        )

    # Return this mapping.
    return hint_name_to_hint


# ....................{ HOOKS                              }....................
# To *EXISTING beartype decorator pipeline integration:
#
# The higher-level callables in ``beartype._decor`` (e.g. ``decormain.py``,
# ``_decor/_call`` currently call ``typing.get_type_hints(...)`` (or a beartype-specific
# equivalent) to resolve forward references, then pass the resulting hints to the
# sanification pipeline (``sanify_hint_root_statement`` and friends). Each of those
# entry points should additionally invoke this module's :func:`._get_type_hint` *RIGHT AFTER*
# the existing forward-reference resolution, producing a pipeline that looks like:
#
#     # 1. Resolve forward references (already done by beartype's existing machinery
#     #    forward-reference machinery in ``beartype._check.forward``.
#     hint_resolved = <existing forward-reference resolver>(...)
#
#     # 2. Recursively expand any PEP 695 type alias wrapping that resolved hint.
#     hint_expanded = _get_type_hint(
#         hint_raw=hint_resolved,
#         exception_prefix=exception_prefix,
#     )
#
#     # 3. Sanify / reduce the now fully-resolved hint as before.
#     hint_sane = sanify_hint_root_statement(
#         hint=hint_expanded,
#         ...
#     )
#
# That two-stage (resolve-then-expand) is the canonical way to hook
# PEP 695 aliases into beartype. Placing the expansion *after* forward-reference
# resolution avoids ever seeing ``TypeAliasType`` objects leaking into the sanification /
# reduction machinery: sanifiers, reducers, and code generators downstream can then simply
# pretend PEP 695 simply does not exist -- because by the time hints reach them.
#
# For code generators downstream can then simply pretend PEP 695 simply does not exist --
# because by the time hints reach them, they are already plain, alias-free hints.


def _apply_expand_type_alias_hook(
    func: Callable[..., Any],
) -> Callable[..., Any]:
    '''
    Trivial example decorator illustrating how a higher-level caller (e.g. the main
    :func:`beartype.beartype` decorator) might hook PEP 695 type-alias
    expansion into its hint-acquisition pipeline.

    This is *NOT` meant to be production code; it is a pedagogical sketch only.
    '''
    # In a real integration point, the higher-level decorator would call
    # ``_get_type_hint`` on each annotation it acquires from ``func`` right
    # before invoking the existing sanification pipeline. For the purposes of this
    # documentation-only sketch we simply return ``func`` unchanged.
    return func
