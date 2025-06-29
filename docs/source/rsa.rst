.. include:: ../common/unsafe.rst

***************
RSA
***************

.. py:module:: toy_crypto.rsa
    :synopsis: Some primative RSA classes

    Imported with::

        import toy_crypto.rsa

Let's see a simple example, from the original publication describing the RSA algorithm. This will require the text decoding scheme used then which is in
:py:func:`toy_crypto.utils.Rsa129.decode`.

.. testcode::

    import toy_crypto.rsa as rsa
    from toy_crypto.utils import Rsa129

    # From the challenge itself
    modulus=114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989075147599290026879543541
    pub_exponent=9007
    ctext=96869613754622061477140922254355882905759991124574319874695120930816298225145708356931476622883989628013391990551829945157815154

    # We have since learned p and q
    p=3490529510847650949147849619903898133417764638493387843990820577
    q=32769132993266709549961988190834461413177642967992942539798288533

    priv_key = rsa.PrivateKey(p, q, pub_exponent = pub_exponent)

    pub_key = priv_key.pub_key
    assert pub_key.N == modulus

    decrypted = priv_key.decrypt(ctext)  # This is a large int

    # Now the Rsa129 text decoder
    ptext = Rsa129.decode(decrypted)
    print(ptext)

.. testoutput::
    
    THE MAGIC WORDS ARE SQUEAMISH OSSIFRAGE


.. autoclass:: PublicKey
    :class-doc-from: both
    :members:
    :undoc-members:


.. autoclass:: PrivateKey
    :class-doc-from: both
    :members:
    :undoc-members:

.. autofunction:: default_e

OAEP utilities
##############

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
--------

RSA keys used with OAEP need to have moduli large enough to handle a couple of hash digests and a few other bytes, so we will use a 1024-bit key for our examples.

.. testcode::
    :hide:

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



Type aliases
-------------

We need to pass some functions around, and so a defining
their types is useful.
For reasons I don't understand, these appear to need to be in
module scope.


.. type:: HashFunc
    :canonical: Callable[[bytes], hashlib._Hash]

    Type for hashlib style hash function.

.. type:: MgfFunc
    :canonical: Callable[[bytes, int, str], bytes]

    Type for RFC8017 Mask Generation Function.

The :class:`Oaep` class
-------------------------

All of the OAEP bits and piece other than the type alias
fit neatly into a class.


.. autoclass:: Oaep
    :members:
    :exclude-members: KNOWN_HASHES, KNOWN_MGFS


.. data:: Oaep.KNOWN_HASHES[str, HashInfo]

    Hashes known for OAEP. keys will be hashlib names.

    .. pprint:: toy_crypto.rsa.Oaep.KNOWN_HASHES
    
.. data:: Oaep.KNOWN_MGFS[str, HashInfo]

    Known mask generatation fubctions.

    .. pprint:: toy_crypto.rsa.Oaep.KNOWN_MGFS
    