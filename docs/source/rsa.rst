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


.. warning::

    The way OAEP decryption errors are reported in this module enable
    chosen ciphertext attacks.
    A proper implemetation must not provide information about why
    decryption failed.
    |project| does not provide a proper implemenation.

Much of the code here attempts to follow :rfc:`8017`,
particularly :rfc:`section 7.1 <8017#section-7.1>`
and :rfc:`appendix B.2 <8017#appendix-B.2>`.
My intention in doing that was to help me better understand OAEP.
This is not intended to be interoperable with things out there in the world.
To whatever extent it is interoperable with the world must not be taken as
an invitation to use it that way.


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