.. include:: ../common/unsafe.rst

Vigenère cipher
===============

.. py:module:: toy_crypto.vigenere
    :synopsis: For when one needs to demonstrate the Vigenère cipher

This module is imported with::

    import toy_crypto.vigenere

.. currentmodule:: toy_crypto.vigenere

The `Vigenère cipher <https://en.wikipedia.org/wiki/Vigenère_cipher>`__ is a historic paper and pencil cipher that when used properly can be easily broken by machine and can be broken by hand though a tedious process.
With improper use it is easy to break by hand.


.. testcode::

    from toy_crypto import vigenere

    alphabet = vigenere.Alphabet.CAPS_ONLY
    cipher = vigenere.Cipher("RAVEN", alphabet)

    plaintext = "ONCE UPON A MIDNIGHT DREARY"
    encrypted = cipher.encrypt(plaintext)

    assert encrypted == "FNXI HGOI E ZZDIMTYT YVRRRT"
    assert cipher.decrypt(encrypted) == plaintext

Proper use (which merely makes this annoying to break by hand instead of easy to break by hand) requires removing any character from the plaintext that is not in the Vigenère alphabet.

.. testcode::


    from toy_crypto import vigenere

    alphabet = vigenere.Alphabet.CAPS_ONLY
    cipher = vigenere.Cipher("RAVEN", alphabet)

    plaintext = "ONCE UPON A MIDNIGHT DREARY"
    plaintext = [c for c in plaintext if c in alphabet]
    plaintext = ''.join(plaintext)

    encrypted = cipher.encrypt(plaintext)
    assert encrypted == "FNXIHGOIEZZDIMTYTYVRRRT"

    decrypted = cipher.decrypt(encrypted)
    print(decrypted)

.. testoutput::

    ONCEUPONAMIDNIGHTDREARY

Using ``Alphabet.PRINTABLE`` will preserve more of the input, as it includes most printiable 7-bit ASCII characters.


The :class:`Cipher` class
----------------------------

A new cipher is created from a key and an alphabet.
If no alphabet is specified the :data:`Alphabet.DEFAULT` is used.

>>> cipher = vigenere.Cipher("RAVEN")
>>> plaintext = "ONCE UPON A MIDNIGHT DREARY"
>>> encrypted = cipher.encrypt(plaintext)
>>> encrypted
'FNXI HGOI E ZZDIMTYT YVRRRT'
>>> cipher.decrypt(encrypted)
'ONCE UPON A MIDNIGHT DREARY'

While a Cipher instance persists the key and the alphabet,
the :meth:`Cipher.encrypt` method starts over at the 0-th element of the key.

>>> cipher = vigenere.Cipher("DEADBEEF", alphabet= "0123456789ABCDEF")
>>> zero_message = "00000000000000000000"
>>> encrypted = cipher.encrypt(zero_message)
>>> encrypted
'DEADBEEFDEADBEEFDEAD'
 >>> new_encrypted = cipher.encrypt("00000")
 >>> assert new_encrypted != 'BEEFD'
 >>> new_encrypted
'DEADB'

.. autoclass:: Cipher
    :members:


The :class:`Alphebet` class
------------------------------

.. autoclass:: Alphabet
    :members:
