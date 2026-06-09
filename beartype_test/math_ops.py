#!/usr/bin/env python3
from functools import wraps
from typing import get_type_hints
from beartype import beartype


def coerce_params(*param_names: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            hints = get_type_hints(func)
            new_args = list(args)
            for i, name in enumerate(func.__code__.co_varnames[:func.__code__.co_argcount]):
                if name in param_names:
                    expected_type = hints.get(name)
                    if expected_type is int:
                        if i < len(new_args):
                            if isinstance(new_args[i], str):
                                try:
                                    new_args[i] = int(new_args[i])
                                except (ValueError, TypeError):
                                    pass
                        elif name in kwargs:
                            if isinstance(kwargs[name], str):
                                try:
                                    kwargs[name] = int(kwargs[name])
                                except (ValueError, TypeError):
                                    pass
            return func(*new_args, **kwargs)
        return wrapper
    return decorator


@coerce_params("a", "b")
@beartype
def divide(a: int, b: int) -> float:
    return a / b
