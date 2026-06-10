#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype :mod:`beartype.vale` validator performance regression unit tests.**

This submodule performs performance regression testing on the public API of the
:mod:`beartype.vale` subpackage, ensuring that custom validators (specifically
:class:`beartype.vale.Is` subscriptions) do not introduce unacceptable runtime
overhead compared to plain type checking.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ class : performance        }....................
class TestIsPerformance:
    '''
    Performance regression tests for :mod:`beartype.vale.Is` validators.

    These tests use :mod:`pytest-benchmark` to compare the runtime overhead of
    custom :class:`beartype.vale.Is` validators against plain type checking,
    ensuring that the additional validation logic does not degrade performance
    beyond acceptable thresholds.
    '''

    def test_plain_int_benchmark(self, benchmark) -> None:
        '''
        Benchmark plain :class:`int` type checking via the
        :func:`beartype.beartype` decorator as a performance baseline.

        This benchmark establishes the reference performance for the most
        trivial type checking scenario: a single :class:`int` parameter
        validated by the :func:`beartype.beartype` decorator.
        '''

        # ....................{ IMPORTS                        }....................
        # Defer test-specific imports.
        from beartype import beartype

        # ....................{ LOCALS                         }....................
        @beartype
        def check_int(x: int) -> int:
            return x

        # ....................{ ASSERTS ~ correctness          }....................
        assert check_int(42) == 42

        # ....................{ ASSERTS ~ performance          }....................
        result = benchmark(check_int, 42)
        assert result == 42

    def test_is_validator_benchmark(self, benchmark) -> None:
        '''
        Benchmark :class:`beartype.vale.Is` validator (subscripted by a lambda
        function) type checking via the :func:`beartype.beartype` decorator.

        This benchmark measures the performance of
        :class:`beartype.vale.Is`\\ [:func:`lambda` ``x: x > 0``] combined with
        :class:`int` type checking, exercising the worst-case scenario where an
        inefficient dynamic callable (a lambda) performs a trivial comparison.
        '''

        # ....................{ IMPORTS                        }....................
        # Defer test-specific imports.
        from beartype import beartype
        from beartype.vale import Is
        from typing import Annotated

        # ....................{ LOCALS                         }....................
        IsPositive = Is[lambda x: x > 0]

        @beartype
        def check_is_positive(x: Annotated[int, IsPositive]) -> int:
            return x

        # ....................{ ASSERTS ~ correctness          }....................
        assert check_is_positive(42) == 42

        # ....................{ ASSERTS ~ performance          }....................
        result = benchmark(check_is_positive, 42)
        assert result == 42

    def test_is_overhead_ratio(self) -> None:
        '''
        Assert that the :class:`beartype.vale.Is` validator execution time
        does not exceed 2x the overhead of plain :class:`int` type checking.

        This test performs repeated measurements of both the plain :class:`int`
        and :class:`beartype.vale.Is` validation paths, then asserts that the
        ratio of their minimum execution times falls within the acceptable
        threshold.
        '''

        # ....................{ IMPORTS                        }....................
        # Defer test-specific imports.
        from beartype import beartype
        from beartype.roar import BeartypeCallHintParamViolation
        from beartype.vale import Is
        from pytest import raises
        from timeit import repeat
        from typing import Annotated

        # ....................{ LOCALS                         }....................
        IsPositive = Is[lambda x: x > 0]

        @beartype
        def func_int(x: int) -> int:
            return x

        @beartype
        def func_is(x: Annotated[int, IsPositive]) -> int:
            return x

        # ....................{ ASSERTS ~ correctness          }....................
        assert func_int(42) == 42
        assert func_is(42) == 42

        with raises(BeartypeCallHintParamViolation):
            func_is(-1)

        # ....................{ ASSERTS ~ performance          }....................
        LOOP_COUNT = 10000
        REPEAT_COUNT = 5

        int_times = repeat(
            lambda: func_int(42), number=LOOP_COUNT, repeat=REPEAT_COUNT)
        is_times = repeat(
            lambda: func_is(42), number=LOOP_COUNT, repeat=REPEAT_COUNT)

        int_min = min(int_times)
        is_min = min(is_times)

        ratio = is_min / int_min
        assert ratio <= 2.0, (
            f'Is[lambda x: x > 0] overhead ({ratio:.2f}x) '
            f'exceeds 2x threshold '
            f'(plain int: {int_min:.4f}s vs Is: {is_min:.4f}s '
            f'over {LOOP_COUNT} iterations)'
        )