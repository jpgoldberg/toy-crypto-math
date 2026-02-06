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
    In particular how particular types are implemented is subject
    to rapid change, as the implementations are
    experimental.

.. note::

    I was unaware of the thrid party
    `anotatted-types <https://pypi.org/project/annotated-types/>`__
    library when I began working on this.
    Much of what I have done poorly reinvents what is there.



Value constrained types
==========================

Since I first started using Python, I have been experimenting with
what are conceptually sub-types of basic types.
Much of the intent is to better document functions through their signatures.
An example is the type signature of :func:`toy_crypto.birthday.probability`,
making use of both :data:`PositiveInt` and :data:`Prob`.

.. code-block:: python

    def probability(
        n: PositiveInt,
        classes: PositiveInt = 365,
        coincident: PositiveInt = 2,
        mode: Mode = "auto",
    ) -> Prob: ...


The types listed here are conceptually narrower sub types of simple types.
For example every :data:`PositiveInt` is an :class:`int`,
but not every  :class:`int` should be considered a :data:`PositiveInt`.

.. autodata:: PositiveInt

.. autodata:: Prob

.. autodata:: Char

.. autodata:: toy_crypto.nt.Modulus
    :no-index:

.. _sec-types-predicates:

Predicates
------------

Predicates are of the type :data:`Predicate`.

.. autodata:: Predicate

And at the moment, several are defined in this and
other modules.

.. autofunction:: is_prob

.. autofunction:: is_positive_int

.. autofunction:: is_char

.. autofunction:: toy_crypto.nt.is_modulus
    :no-index:



Generating predicates
-----------------------

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
    >>> from toy_crypto.types import ValueRange, make_predicate, LengthRange

    >>> Five2ten = Annotated[int, ValueRange(5, 10)]
    >>> is_5to10 = make_predicate("is_5to10", Five2ten)

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
    >>> is_5to10('five')
    False

Constraints
------------

The example above illustrates :func:`ValueRange` for setting a constraint 
on the type, ``Five2ten`` through its declaration.
Another constraint defined in this module is :func:`LengthRange`.

.. doctest::

    >>> Password = Annotated[str, LengthRange(min=8, max=None)]
    >>> is_password = make_predicate('is_password', Password)

    >>> too_short = 'abcdefg'
    >>> len(too_short)
    7
    >>> is_password(too_short)
    False

    >>> eight_chars = 'ABCDEFGH'
    >>> len(eight_chars)
    8
    >>> is_password(eight_chars)
    True

    >>> very_long = "spam, spam, spam, eggs, bacon, and spam" * 20
    >>> len(very_long)
    780
    >>> is_password(very_long) # There is no upper limit on length
    True

.. autoclass:: ValueRange
    :class-doc-from: init
    :members:

.. autoclass:: LengthRange
    :class-doc-from: init
    :members:

Constraints must all be a subclass of abstract class
:class:`Constraint`,
and implement the method :func:`Constraint.is_valid`.

.. autoclass:: Constraint
    :members:

As illustrated above, a predicate can be created from an appropriate annotated type alias using :func:`make_predicate`.

.. autofunction:: make_predicate

The generated predicate will return false for its argument unless all constraints are met.
Predicates are of the type :data:`Predicate`.


Creating TypeGuards
-------------------

In this section everything I say about `TypeGuard`_ applies to
`TypeIs`_. There are differences between the two that are not
relevant for this discussion or my examples beyond that fact that
`TypeIs`__` was introduced in Python 3.13, and I don't want to raise
the minimum of this package just yet.

.. _TypeIs: https://docs.python.org/3/library/typing.html#typing.TypeIs

.. _TypeGuard: https://docs.python.org/3/library/typing.html#typing.TypeGuard

Much of this module is what I could salvage from my misguided attempt
to automate the generation of TypeGuards.
The separation between Python itself and type checking system
doomed my efforts from the start.
I should have foreseen that.

At any rate here is an example of creating a `TypeGuard`.

.. testcode:: python

    from typing import NewType, TypeGuard, reveal_type
    from toy_crypto.types import make_predicate, ValueRange
    Probability = NewType("Probability", float)

    _inner_is_probability = make_predicate(
                "is_probability", # Final name here for setting name and docs
                Probability,      # this will end up being a check for float
                [ValueRange(0.0, 1.0)],  # Constraints
            )
    
    def is_probability(val: object) -> TypeGuard[Probability]:
        return _inner_is_probability(val)
    
    # And now give our TypeGuard predicate's documentation
    is_probability.__doc__ = _inner_is_probability.__doc__

    p = 0.5
    assert is_probability(p)
    reveal_type(p)  # type checker says Probability, run-tine float

.. testoutput::

    float