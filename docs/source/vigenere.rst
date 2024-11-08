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

    assert encrypted == "FNXI LPJR R HMQEIBLG DMINIY"
    assert cipher.decrypt(encrypted) == plaintext



The :mod:`vigenere` functions
------------------------------

.. automodule:: toy_crypto.vigenere
    :members:
