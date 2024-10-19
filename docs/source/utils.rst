.. include:: ../common/unsafe.rst

Utility functions
=================

This are imported with:

    import toy_crypto.utils


.. autofunction:: toy_crypto.utils.digit_count

Coding this is a math problem, not a string representation problem.
Idetally the solution would be to use

..  math:: d = \lfloor\log_b \| x \| + 1\rfloor

but that leads to erroneous results due to the precision limitations
of :py:func:`math.log`.

>>> from toy_crypto.utils import digit_count
>>> digit_count(999)
3
>>> digit_count(1000)
4
>>> digit_count(1001)
4
>>> digit_count(9999999999999998779999999999999999999999999999999999999999999)
61
>>> digit_count(9999999999999999999999999999999999999999999999999999999999999)
61
>>> digit_count(10000000000000000000000000000000000000000000000000000000000000)
62
>>> digit_count(0)
1
>>> digit_count(-10_000)
5

.. autofunction:: toy_crypto.utils.lsb_to_msb

:func:`~toy_crypto.utils.lsb_to_msb` is used by
:func:`~toy_crypto.ec.Point.scaler_multiply` and would be used by modular exponentiation
for implementations of those that leak the bits of the scalar (or exponent)
through side channels. 

>>> from toy_crypto.utils import lsb_to_msb
>>> list(lsb_to_msb(13))
[1, 0, 1, 1]


.. autofunction:: toy_crypto.utils.xor

>>> from toy_crypto.utils import xor
>>> message = b"Attack at dawn!"
>>> pad = bytes(10) + bytes.fromhex("00 14 04 05 00")
>>> modified_message = xor(message, pad)
>>> modified_message
b'Attack at dusk!'
 
.. autoclass:: toy_crypto.utils.Rsa129
    :members: