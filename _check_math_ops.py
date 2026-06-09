from beartype_test.math_ops import divide, divide_lenient
from beartype.roar import BeartypeCallHintParamViolation

assert divide(10, 2) == 5.0
print('PASS: divide(10, 2) == 5.0')

try:
    divide('10', 2)
    assert False, 'should have raised'
except BeartypeCallHintParamViolation:
    print('PASS: divide("10", 2) raises BeartypeCallHintParamViolation')

assert divide_lenient(10, 2) == 5.0
print('PASS: divide_lenient(10, 2) == 5.0')

assert divide_lenient('10', 2) == 5.0
assert divide_lenient(10, '2') == 5.0
assert divide_lenient('10', '2') == 5.0
print('PASS: divide_lenient accepts numeric strings')

try:
    divide_lenient('not_a_number', 2)
    assert False, 'should have raised'
except BeartypeCallHintParamViolation:
    print('PASS: uncoercible string raises BeartypeCallHintParamViolation')

try:
    divide_lenient(None, 2)
    assert False, 'should have raised'
except BeartypeCallHintParamViolation:
    print('PASS: None raises BeartypeCallHintParamViolation')

result = divide_lenient('10', 2)
assert isinstance(result, float)
print('PASS: divide_lenient returns float')

print()
print('All manual checks passed.')
