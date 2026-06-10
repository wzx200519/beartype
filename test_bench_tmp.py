import pytest
def test_bench(benchmark):
    def f(): pass
    benchmark(f)
    print(benchmark.stats)
    print(dir(benchmark.stats))
    print(benchmark.stats.stats.mean)
