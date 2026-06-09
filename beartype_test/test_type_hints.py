def test_validate_and_convert() -> None:
    from beartype_test._helpers import (
        test_validate_and_convert_inline,
        validate_and_convert,
    )

    assert validate_and_convert([1, '2', '3'], 0.5) == [0.5, 1.0, 1.5]
    assert validate_and_convert([4, '5']) == [4.0, 5.0]

    test_validate_and_convert_inline()
