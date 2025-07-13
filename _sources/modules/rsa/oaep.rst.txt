.. include:: /../common/unsafe.rst

.. currentmodule:: toy_crypto.rsa


##############
OAEP
##############

Imported with

.. testcode::

    from toy_crypto import rsa


Primitive RSA is deterministic,
so it completely fails to provide IND-CPA security.
It is also vulnerable to chosen ciphertext attacks. 
:wikipedia:`OAEP (Optimized Assymmetric Encryption Padding) <Optimal asymmetric encryption padding>`
is designed to address both of those when *properly implemented*.
This module does *not* provide a proper implemenation.


Much of the code here attempts to follow :rfc:`8017`,
particularly :rfc:`section 7.1 <8017#section-7.1>`
and :rfc:`appendix B.2 <8017#appendix-B.2>`.
My intention in doing that was to help me better understand OAEP.
This is not intended to be interoperable with things out there in the world.
To whatever extent it is interoperable with the world must not be taken as
an invitation to use it that way.

Examples
=========

RSA keys used with OAEP need to have moduli large enough to handle a couple of hash digests and a few other bytes, so we will use a 1024-bit key for our examples.

.. testcode::
    :hide:

    from toy_crypto import rsa

    p1024 = bytes.fromhex(
        "ec f5 ae cd 1e 55 15 ff fa cb d7 5a 28 16 c6 eb" 
        "f4 90 18 cd fb 46 38 e1 85 d6 6a 73 96 b6 f8 09"
        "0f 80 18 c7 fd 95 cc 34 b8 57 dc 17 f0 cc 65 16" 
        "bb 13 46 ab 4d 58 2c ad ad 7b 41 03 35 23 87 b7"
        "03 38 d0 84 04 7c 9d 95 39 b6 49 62 04 b3 dd 6e"
        "a4 42 49 92 07 be c0 1f 96 42 87 ff 63 36 c3 98"
        "46 58 33 68 46 f5 6e 46 86 18 81 c1 02 33 d2 17"
        "6b f1 5a 5e 96 dd c7 80 bc 86 8a a7 7d 3c e7 69"
    )

    q1024 = bytes.fromhex(
        "bc 46 c4 64 fc 6a c4 ca 78 3b 0e b0 8a 3c 84 1b"
        "77 2f 7e 9b 2f 28 ba bd 58 8a e8 85 e1 a0 c6 1e" 
        "48 58 a0 fb 25 ac 29 99 90 f3 5b e8 51 64 c2 59" 
        "ba 11 75 cd d7 19 27 07 13 51 84 99 2b 6c 29 b7" 
        "46 dd 0d 2c ab e1 42 83 5f 7d 14 8c c1 61 52 4b"
        "4a 09 94 6d 48 b8 28 47 3f 1c e7 6b 6c b6 88 6c" 
        "34 5c 03 e0 5f 41 d5 1b 5c 3a 90 a3 f2 40 73 c7"
        "d7 4a 4f e2 5d 9c f2 1c 75 96 0f 3f c3 86 31 83"
    )
    
    p = rsa.Oaep.os2ip(p1024)
    q = rsa.Oaep.os2ip(q1024)

    # Don't run this check every time
    # from toy_crypto.nt import isprime
    # assert isprime(p)
    # assert isprime(q)

    key2048 = rsa.PrivateKey(p, q)
    # assert  2048 - 7 < key2048.pub_key.N.bit_length() <= 2048

:data:`key2048` is a 2048-bit private key already set up in some undisplayed code.

Just showing that the key exists and is the right size.

.. testcode::

    # key2048 = ...
    pub2048 = key2048.pub_key
    assert  2048 - 7 < pub2048.N.bit_length() <= 2048

And lets demo an unfortunate (unless you are an attacker) property of primitive 
RSA.
Our primitive encryption and decryption functions take and yield integers

.. testcode::

    message = b"My hovercraft is full of eels"
    i_message = rsa.Oaep.os2ip(message)

    prim_ctext1 = pub2048.encrypt(i_message)
    assert key2048.decrypt(prim_ctext1)

So far so good, but sadly, the encryption of the same
message always yields the same ciphertext.

.. testcode::

    # same key and message as above
    prim_ctext2 = pub2048.encrypt(i_message)
    assert prim_ctext2 == prim_ctext1

.. testcode::

    # same message and keys as above
    oaep_ctext1 = pub2048.oaep_encrypt(message)
    decrypted1 = key2048.oaep_decrypt(oaep_ctext1)
    assert decrypted1 == message

    oaep_ctext2 = pub2048.oaep_encrypt(message)
    decrypted2 = key2048.oaep_decrypt(oaep_ctext2)
    assert decrypted2 == message

    # but now we see that the two ciphertexts are different
    assert oaep_ctext1 != oaep_ctext2


A (very limted) choice of hashes
=================================

For my purposes, I could have just hardcoded use of
:py:func:`hashlib.sha256` or a more modern one,
but most of published test vectors
for RSA-OAEP use :py:func:`hashlib.sha1`.

For reasons I don't understand, I had difficulty
getting these type definition within the :class:`Oaep` class,
so those are given module scope.

.. type:: HashFunc
    :canonical: Callable[[bytes], hashlib._Hash]

    Type for hashlib style hash function.

.. type:: MgfFunc
    :canonical: Callable[[bytes, int, str], bytes]

    Type for RFC8017 Mask Generation Function.

The (short) lists of supported hash and mask generation functions
are attributes of the :class:`Oaep` class, as are the classes to describe them.
Also note that these are more sanely  and readably defined than
what may appear in the automatically generated documentation.

.. autoattribute:: Oaep.KNOWN_HASHES
    :no-index:
    :no-value:

    .. pprint:: toy_crypto.rsa.Oaep.KNOWN_HASHES
    
.. autoattribute:: Oaep.KNOWN_MGFS
    :no-index:
    :no-value:

    .. pprint:: toy_crypto.rsa.Oaep.KNOWN_MGFS
    
Integers, octet-streams, and masks
----------------------------------

Primitive RSA operations on integers, but OAEP is designed for
encryption and decryption of sequences of :py:class:`bytes`,
or octet-streams in the parlence of the standards.
The standards define two functions, ``I2OSP`` and ``OS2IP`` for those
conversions. I don't implement them as in the standards, but use Python standard library utililties. So class methods :meth:`Oaep.i2osp` and
:meth:`Oaep.os2ip` are wrappers for standard library method
:py:meth:`int.to_bytes` and class method :py:meth:`int.from_bytes`.

.. automethod:: Oaep.i2osp
    :no-index:

.. automethod:: Oaep.os2ip
    :no-index:


.. figure:: /images/Big-endian-Chena-320x320.png
    :align: center
    :alt: A dog with a big rear-end

    Chena, like all operations in this class, is big-endian;
    although in her case it is her rear end is bigger than her bytey end.


The security that OEAP offers comes from the clevernesss of applying a mask
to the plaintext, while keeping the seed for the mask out of the clear.
The mask is generated by a mask generation function,
``MGF1`` in the standards.
It is a lot like :rfc:`HKDF <5869>`,
which probably would have used had it been around when OAEP was first developed.

.. automethod:: Oaep.mgf1 
    :no-index:


The API
---------------------------------

OAEP encryption and decryption performed with method on instances of the
:class:`.PublicKey` and :class:`.PrivateKey` respectively.

.. automethod:: PublicKey.oaep_encrypt
    :no-index:

.. automethod:: PrivateKey.oaep_decrypt
    :no-index:


.. autoclass:: Oaep
    :members:

