#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Pedagogical demo of the new** ``_get_type_hint`` **/ ``_expand_type_alias``
**PEP 695 pipeline.**

This module is intentionally *NOT* imported by :mod:`beartype` itself; it is
provided solely as a self-contained, runnable illustration of how the new
``_get_type_hint`` hook is wired into a ``@beartype``-style decorator so that
users can see the feature working end-to-end in a few lines.

Run this file directly under Python 3.12+ to see:

    * a chain of ``type`` statements being expanded to their concrete base;
    * a self-referential (``type A = B; type B = A``) pair of aliases being
      detected *before* infinite recursion occurs;
    * a parameterized ``type Generic[T] = list[T]`` alias being preserved as a
      ``GenericAlias`` (because its ``__origin__`` carries the user-supplied
      type arguments).
'''

# ....................{ IMPORTS                            }....................
import sys
from beartype._check.check import _get_type_hint

# ....................{ MAIN                               }....................
def _main() -> None:
    print('[pep695-demo] Python', sys.version.split()[0])

    # ------------------------------------------------------------------ #
    # CASE 1: a plain chain of ``type`` aliases that should collapse to int #
    # ------------------------------------------------------------------ #
    exec(
        '''
type C = int
type B = C
type A = B
''',
        globals(),
    )
    # ``A`` is a ``TypeAliasType`` whose ``__value__`` transitively points to ``int``.
    expanded = _get_type_hint(hint_raw=A, exception_prefix='[chain] ')  # type: ignore[name-defined]  # noqa: F821
    print(f'  chain:  A -> B -> C -> int  =>  {expanded!r}')
    assert expanded is int, f'expected int, got {expanded!r}'

    # ------------------------------------------------------------------ #
    # CASE 2: a self-referential pair: ``type A = B; type B = A``         #
    # ------------------------------------------------------------------ #
    ns_selfref: dict = {}
    exec(
        '''
type A = B
type B = A
''',
        ns_selfref,
    )
    A_self = ns_selfref['A']
    expanded_self = _get_type_hint(
        hint_raw=A_self, exception_prefix='[selfref] ')
    print(f'  selfref: A <-> B => {expanded_self!r}')
    # The cycle-breaker returns the alias itself rather than blowing the stack.
    assert expanded_self is A_self, (
        f'cycle-breaker should have returned alias itself, got {expanded_self!r}'
    )

    # ------------------------------------------------------------------ #
    # CASE 3: a parameterized alias: ``type Generic[T] = list[T]``        #
    # ------------------------------------------------------------------ #
    ns_gen: dict = {}
    exec(
        '''
type Generic[T] = list[T]
''',
        ns_gen,
    )
    Generic = ns_gen['Generic']
    # ``Generic[int]`` is a ``types.GenericAlias``, NOT a ``TypeAliasType``, and
    # therefore must be passed through unchanged so beartype's existing generic
    # machinery can handle the type arguments.
    parameterized = Generic[int]  # type: ignore[valid-type]
    expanded_param = _get_type_hint(
        hint_raw=parameterized, exception_prefix='[generic] ')
    print(f'  generic: Generic[int] => {expanded_param!r}')
    assert expanded_param is parameterized, (
        'parameterized aliases must pass through unchanged'
    )

    print('[pep695-demo] all cases passed')


if __name__ == '__main__':
    _main()
