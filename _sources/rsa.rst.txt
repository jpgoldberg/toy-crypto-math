.. include:: ../common/unsafe.rst

RSA
==============


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
