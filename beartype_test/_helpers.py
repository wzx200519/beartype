import pytest
from beartype import beartype
from beartype.roar import BeartypeException

@beartype
def validate_and_convert(items: list[int | str], factor: float = 1.0) -> list[float]:
    """
    Validates the input list and converts elements to float after multiplying by factor.
    String elements are converted to int first.
    """
    result = []
    for item in items:
        if isinstance(item, str):
            item = int(item)
        result.append(float(item * factor))
    return result

def test_validate_and_convert_exception():
    """
    Test that validate_and_convert raises BeartypeException when passed a list containing a float.
    Uses assert to ensure the exception is actually raised.
    """
    with pytest.raises(BeartypeException) as excinfo:
        validate_and_convert([1, 2.5, "3"])
    
    assert "float" in str(excinfo.value) or "2.5" in str(excinfo.value)

if __name__ == "__main__":
    assert validate_and_convert([1, "2", 3], factor=2.0) == [2.0, 4.0, 6.0]
    test_validate_and_convert_exception()
    print("All tests passed!")
