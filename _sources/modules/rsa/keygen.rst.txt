.. include:: /../common/unsafe.rst

*******************
RSA Key Generation
*******************

.. currentmodule:: toy_crypto.rsa

This page describes *some* of things that are part of
the :mod:`toy_crypto.rsa` module.
They are imported with::
 
        from toy_crypto import rsa

Not every pair of primes, :math:`(p, q)`,
is suitable for creating a good :class:`.PrivateKey`.
With public modulus :math:`N = pq`, and public exponent, *e*,
some of the conditions that should hold of them are

- They should be large enough so that *N* is the desired bit size;
- They should each be not much less then :math:`\sqrt{N}`;
- But they shouldn't be too close to each other, either;
- The totient of *N* must be relatively prime to the public exponent, *e*.
  That is :math:`\gcd(p - 1, e)` and :math:`\gcd(q - 1, e)` must each be 1.

The prime generation function defined in 
appendix A.1.3 FIPS 186-B :cite:`FIPS-186-5`
guarentees those conditions are met.
It is clever in that it checks those conditions on candidate primes
before testing whether those candidates are prime,
which is a much more computationally expensive test.

The algorithm defined in
§6.3.1} of NIST-SP-56b :cite:`NIST-SP800-56b`
imposes the additional condition that the secret
decryption exponent, *d*, of a private key is not less than
:math:`\sqrt{N}`.


The functions in this module,
:func:`.fips186_prime_gen` and :func:`.key_gen`,
partially follow those specifications,
but they do not enforce the minimum strength
specifications (2048-bit moduli).
I want to be able to generate some extremely weak
keys for demonstration purposes.

.. note::

    Even if functions here faithfully followed the standards
    (which they don't) it would not mean that the implenetations
    would be secure.

Examples
=========

.. testcode:: keygen
    :hide:

    from toy_crypto import rsa

So that documentation building doesn't take too long, we
will use a tiny key size.

.. testcode:: keygen


    # Do not use RSA keys smaller than 2048 bits,
    # Do as I say, not as I do
    pub_key, priv_key = rsa.key_gen(strength=56, key_size=512)
    assert pub_key.N.bit_length() == 512

Now we set up a message to encrypt with the tiny key.
Any integer we encryption with a 512 bit key must be less than :math:`2^{512}`.
OAEP padding (with SHA1) would take up 322 bits, so we will just use
primitive RSA.

.. testcode:: keygen

    message = int.from_bytes(b"Attack @ dusk!")
    assert message.bit_count() < 512

    ctext = pub_key.encrypt(message)
    decrypted = priv_key.decrypt(ctext)
    assert message == decrypted

The API
=========

.. autofunction:: fips186_prime_gen

.. autofunction:: key_gen

.. autofunction:: estimate_strength
