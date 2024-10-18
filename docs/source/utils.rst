.. include:: ../common/unsafe.rst

Utility functions
=================

This are imported with:

    import toy_crypto.utils


.. autofunction:: toy_crypto.utils.digit_count

Coding this is a math problem, not a string representation problem.
The solution used here is

..  math:: d = \lfloor\log_b \| x \| + 1\rfloor

Unfortunately, doing this the mathy way leaves us reliant the the precision
of :py:func:`math.log`.

>>> from toy_crypto.utils import digit_count
>>> digit_count(999)
3
>>> digit_count(1000)
4
>>> digit_count(1001)
4
>>> digit_count(9999999999999998779999999999999999999999999999999999099999999)
61
>>> digit_count(9999999999999998789999999999999999999999999999999999099999999), "oops!"
(62, 'oops!')
>>> "The correct answer is 61"
'The correct answer is 61'

.. autofunction:: toy_crypto.utils.lsb_to_msb

.. autofunction:: toy_crypto.utils.xor
   
