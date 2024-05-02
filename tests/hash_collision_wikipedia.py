file_contents = """bits,10e-18,10e-15,10e-12,10e-9,10e-6,0.01,0.1,0.25,0.5,0.75
16,2,2,2,2,2,11,36,190,300,430
32,2,2,2,3,93,2900,9300,50,000,77,000,110,000
64,6,190,6100,190,000,6,100,000,1.9e8,6.1e8,3.3e9,5.1e9,7.2e9
128,2.6e10,8.2e11,2.6e13,8.2e14,2.6e16,8.3e17,2.6e18,1.4e19,2.2e19,3.1e19
256,4.8e29,1.5e31,4.8e32,1.5e34,4.8e35,1.5e37,4.8e37,2.6e38,4.0e38,5.7e38
384,8.9e48,2.8e50,8.9e51,2.8e53,8.9e54,2.8e56,8.9e56,4.8e57,7.4e57,1.0e58
512,1.6e68,5.2e69,1.6e71,5.2e72,1.6e74,5.2e75,1.6e76,8.8e76,1.4e77,1.9e77"""


csvfile = file_contents.split("\n")

probs = [float(p) for p in csvfile[0].split(",")[1:]]

rows: list[list[int]] = []

for r in csvfile[1:]:
    rows.append([int(float(n)) for n in r.split(",")])

# Now construct list of triples of (bits, prob, n)

# We need our indicies because I didn't set these up as dicts

vectors: list[tuple[int, float, int]] = []  # (bits, prop, n)
for r in rows:
    bits = r[0]
    for i, p in enumerate(probs):
        vectors.append((bits, probs[i], r[i + 1]))

print(vectors)
