.. include:: /../common/unsafe.rst

########
Types
########

Imported with::

    import toy_crypto.types

.. currentmodule:: toy_crypto.types

.. note::

    The name of this module is the same as a standard library
    `types module <https://docs.python.org/3/library/types.html>`__,
    so be sure to pay attention to name spaces if
    you choose to import this.

.. warning::

    Many things in this module should be consider unstable.
    In particular things like :type:`Prob` are currently implemented
    as :class:`typing.Annotated`.
    As such these are indistinguisable from their base types with respect
    to static type checking.
    But in future they may be implemented as :class:`typing.NewType`.
    This impacts the behavior of their corresponding predicates,
    such as :func:`is_prob`,
    which currently play no role in type narrowing.


Annotated types
==================

The types listed are conceptually narrower sub types of simple types.
For example every :data:`PositiveInt` is an :class:`int`,
but not every  :class:`int` should be considered a :data:`PositiveInt`.

.. autodata:: PositiveInt

.. autodata:: Prob

.. autodata:: Char

.. _sec-types-predicates:

Predicates
============

.. autofunction:: is_prob

.. autofunction:: is_positive_int

.. autofunction:: is_char

Generating predicates
=======================

The predicates listed in :ref:`sec-types-predicates` are generated
from the information in the annotated types.
There is no good reason for this other than me wanting to play
around to see how to do so.

The mechanism is limited and experimental. If you want to generate
types in Python using robust and well-designed tools consider something like
`cattrs <https://catt.rs/en/stable/>`__ or `Pydantic <https://docs.pydantic.dev/latest/>`__.

To illustrate, let's create a ``Five2ten`` that will be an integer
between 5 and 10 inclusively.

.. doctest::

    >>> from typing import Annotated
    >>> from toy_crypto.types import ValueRange, make_predicate

    >>> Five2ten = Annotated[int, ValueRange(5, 10)]
    >>> is_5to10 = make_predicate(Five2ten)

    >>> is_5to10(7)
    True
    >>> # Boundries are included
    >>> is_5to10(5)
    True
    >>> is_5to10(4)
    False
    >>> is_5to10(10)
    True
    >>> is_5to10(11)
    False
    >>> # Must be an int
    >>> is_5to10(7.0)
    False

