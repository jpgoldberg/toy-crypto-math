import timeit
import json
import polars as pl

# import cProfile
from toy_crypto.sieve import BaSieve, IntSieve, SetSieve, Sievish

repetitions = 1


def sieve_count(s_class: Sievish, size: int) -> int:
    s_class._reset()
    s = s_class.from_size(size)
    return s.count


sizes: list[int] = [10**n for n in range(2, 7)]
sizes += [5 * (10**n) for n in range(1, 6)]

s_classes: list[str] = [f"{c.__name__}" for c in (BaSieve, IntSieve, SetSieve)]

results: dict[str, list[float] | list[int]] = {"size": sizes}

for sieve_type in s_classes:
    times: list[float] = []
    for size in sizes:
        stmt = f"sieve_count({sieve_type}, {size})"
        t = timeit.timeit(stmt=stmt, number=repetitions, globals=globals())
        times.append(t)
    results[sieve_type] = times

j = json.dumps(results, indent="\t")

jfilename = "timings.json"
with open(jfilename, "w", encoding="utf-8") as f:
    f.write(j)
print(j)

df = pl.DataFrame(results)
print(df)

cfilename = "timings.csv"
df.write_csv(cfilename)
