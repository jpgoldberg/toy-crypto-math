# example ec from Serious Cryptography

p = 191
FF = GF(p)
A = -4 % p
B = 0

EC=EllipticCurve(FF , [A, B])

def ec_coord(P):
    """Coordinates of point as integer list.
    
    In which I try to learn to live with Duck typing.
    """

    if P.is_zero():
        raise ValueError("P should not be point at infinity")

    try:
        pxy =P.xy()
    except AttributeError:
        raise TypeError("P doesn't have xy coordinates")
    
    pxy = list(pxy)
    if not all(z == int(z) for z in pxy):
        raise TypeError("coordinates must be integral")

    return [int(x) for x in list(pxy)]

# Get a generator

g = EC.gens()[0]
print(f'base point as at {g.xy()}')

order = g.order()
print(f'Generator order is {order}')

# construct test vectors
vectors: dict[int, tuple[int, int]] = {}
for d in range(1, order):
    vectors[d] = (d * g).xy()

print(vectors)