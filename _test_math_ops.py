import sys
sys.path.insert(0, '.')
from beartype_test.math_ops import divide, divide_lenient
from beartype.roar import BeartypeCallHintParamViolation

print('--- divide(10, 2) =', divide(10, 2))
print('--- divide("10", 2) =', divide('10', 2))
print('--- divide("10", "2") =', divide('10', '2'))
print('--- divide(a="10", b="2") =', divide(a='10', b='2'))

try:
    divide('abc', 2)
except BeartypeCallHintParamViolation as e:
    print('--- divide("abc", 2) raised BeartypeCallHintParamViolation')

try:
    divide(10, 'xyz')
except BeartypeCallHintParamViolation as e:
    print('--- divide(10, "xyz") raised BeartypeCallHintParamViolation')

try:
    divide(10.5, 2)
except BeartypeCallHintParamViolation as e:
    print('--- divide(10.5, 2) raised BeartypeCallHintParamViolation')

try:
    divide_lenient('abc', 2)
except BeartypeCallHintParamViolation as e:
    print('--- divide_lenient("abc", 2) raised BeartypeCallHintParamViolation')

print('--- divide_lenient("10", 2) =', divide_lenient('10', 2))
print('--- divide.__name__ =', divide.__name__)
