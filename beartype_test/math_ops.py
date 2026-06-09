from beartype import beartype
from beartype.roar import BeartypeCallHintViolation
from functools import wraps


def coerce_str_to_int(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        new_args = []
        for i, arg in enumerate(args):
            if isinstance(arg, str):
                try:
                    arg = int(arg)
                except ValueError:
                    raise BeartypeCallHintViolation(
                        f'Cannot convert string "{args[i]}" to int'
                    ) from None
            new_args.append(arg)

        new_kwargs = {}
        for key, val in kwargs.items():
            if isinstance(val, str):
                try:
                    val = int(val)
                except ValueError:
                    raise BeartypeCallHintViolation(
                        f'Cannot convert string "{kwargs[key]}" to int'
                    ) from None
            new_kwargs[key] = val

        return func(*new_args, **new_kwargs)
    return wrapper


@coerce_str_to_int
@beartype
def divide(a: int, b: int) -> float:
    return a / b