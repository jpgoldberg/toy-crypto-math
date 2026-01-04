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


Predicates
============

.. autofunction:: is_prob







