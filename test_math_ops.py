#!/usr/bin/env python3
from beartype_test.math_ops import divide

# Test 1: normal int inputs
print('divide(10, 2) =', divide(10, 2))

# Test 2: string inputs that can be converted
print('divide("10", 2) =', divide("10", 2))

# Test 3: keyword arguments with strings
print('divide(a="20", b="4") =', divide(a="20", b="4"))

# Test 4: non-convertible string should still raise beartype exception
try:
    divide("abc", 2)
except Exception as e:
    print('divide("abc", 2) raised:', type(e).__name__)

# Test 5: wrong type that is not string should raise beartype exception
try:
    divide(3.14, 2)
except Exception as e:
    print('divide(3.14, 2) raised:', type(e).__name__)
