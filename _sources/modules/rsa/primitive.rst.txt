.. include:: /../common/unsafe.rst

***************
Primitive RSA
***************

.. currentmodule:: toy_crypto.rsa


This page describes *some* of things that are part of
the :mod:`toy_crypto.rsa` module.
They are imported with::
 
        from toy_crypto import rsa

Primitive RSA, as illustrated here, operates on integers and is deterministic.
The former makes it impractical for direct use and the latter means that
it immediately fails to meet ``IND-CPA`` security.
See :doc:`oaep` for discussion of and illustration of how those are properly addressed.


The original example
=====================

Let's see a simple example, from the original publication describing the RSA algorithm :cite:`Gardner77:RSA`. This will require the text decoding scheme used then which is in
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

Primitive API
==============

.. autoclass:: PublicKey
    :class-doc-from: both
    :members:


.. autoclass:: PrivateKey
    :class-doc-from: both
    :members:

