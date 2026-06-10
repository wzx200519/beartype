import timeit
from beartype.vale import Is

is_positive = Is[lambda x: x > 0]

def normal_check():
    return isinstance(1, int)

def custom_check():
    return is_positive.is_valid(1)

normal_time = timeit.timeit(normal_check, number=1000000) / 1000000
custom_time = timeit.timeit(custom_check, number=1000000) / 1000000

print(f"Normal: {normal_time * 1e9:.2f} ns")
print(f"Custom: {custom_time * 1e9:.2f} ns")
print(f"Ratio: {custom_time / normal_time:.2f}x")
