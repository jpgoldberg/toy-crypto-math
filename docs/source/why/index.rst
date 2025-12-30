.. include:: /../common/unsafe.rst

.. currentmodule:: toy_crypto

*************
Motivation
*************

There are two facts to keep in mind when considering why something like this
toy cryptography project should exist:

1. Python is great for illustrating (some) cryptographic concepts.
2. Python is terrible for developing secure implementations.


Python is great
===============

Pseudocode that runs
---------------------

Python code can be highly readable, even to people with limited programming experience.
Indeed, the oldest (and most poorly coded) module here, :mod:`.ec`, exists because I wanted to
illustrate the Double and Add approach to :meth:`.ec.scaler_multiply`.
I thought it would be fun if my pseudo-code would actually run.

One :py:class:`int` to Rule Them All
-------------------------------------

Nearly everyone I know with a math background complains about two things when they first learn a (typical) programming language.
The first is that ``=`` is an assignment
instead of just a statement of equality.
The second is when they discover that something of type ``int``
is strictly limited in size and is not actually an Integer.
Python solves this latter problem,
and more importantly makes it easy to present code that deals with
larger integers.

I had previously attempted to use Golang to illustrate algorithms,
but found that the clutter of
`big.NewInt() <https://pkg.go.dev/math/big@go1.24.5#NewInt>`__ was just distracting.

And Python is terrible
======================

Python is not well-suited for secure cryptographic implementations,
which is why things like pyca_ are mostly written in C or Rust.
Efficiency and defense against many side challenges require direct manipulation
of bytes and integer types that are closer to the machine.
Python, by design, does not offer direct access to memory management or low level data types.
This design helps Python be as readable as it is, but it does have consequence for cryptographic implementations.
This also impacts what Python is suitable for illustrating.
I have (so far) chosen to not implement algorithms that depend heavily
on bitwise manipulation.

Additionally, all Python objects,
including imported non-builtin modules,
can be read even modified at run time.
Again there are reasons why Python, an interpreted language,
is designed this way.
Modules and code is expected to behave politely, but there is no enforcement
of that within the language itself.

Fortunately I am not attempted to provide secure implementations of anything.

Early motivation
================

My initial goals for what what became different modules varied,

- :mod:`.birthday` originated because I had need for the calculations.
- :mod:`.sec_games` exists because a presentation I gave intending to explain ``IND-CPA`` had failed, and I hope that providing illustrations of the game in action will help for next time.
- :mod:`.ec` originated because I wanted to illustrate the “double and add” algorithm for scaler multiplication of a point.
- :mod:`.rsa` had its origins in me wanted to provide a walk through of Adversary in the Middle Attack with small numbers. It has now been expanded because, among other things, I wanted to understand OAEP better.
- :mod:`.types` and some of the run time type checking exists because when I first started to play with Python I reacted badly to its type system. (I will probably remove much of that run time type checking in future versions.)
- :mod:`.nt` exists because I didn't know that sympy_ was pure Python and I did want illustrate some of the algorithms themselves in presentation slides.

Other modules have their own peculiar origin stories.

Eventually I realized that I should gather this into a single
repository and super module.
After all,
I had probably written the Extended Euclidean Algorithm half a dozen times,
and I was getting tired of not finding my previous implementations.
And as I wanted to include these in Jupyter notebooks, I published on PyPI
(because I didn't know at the time that pip could install packages from a public git repository.)

That was then. This is now
---------------------------

I do believe that what is here can be genuinely useful,
particularly for those teaching or learning about some
aspects of cryptography.
The :mod:`.sec_games` module is not
something I've seen elsewhere and provides a mechanism for
teaching about *Modern* Cryptography.
The :mod:`.birthday` modules provides ways to calculate things that
people working with or adjacent to Cryptography might want to calculate.

Coding style
-------------

Although some of the code here is from when I first started playing with Python,
my intent is for readable code.
However, one person's readable code
is another person's too clever by half trickery.
So I will mention some things might be unfamiliar to novice programers
or those with limited Python experience.

1. Comprehensions
    Things like
    `list Comprehensions <https://docs.python.org/3/glossary.html#term-list-comprehension>`__
    are just such a great thing that Python offers that I couldn't
    bring myself to use explicit ``for`` loops where a comprehension
    is more expressive\ [#expressive]_ of intent.
    And they are such a great thing, that you should become familiar with them
    anyway.

2. Generators and Iterators.
    These are functions that instead of producing, say, a list
    will compute and produce each element of the list in turn.
    I am not particular consistent in when I use one instead of the
    other.

3. Abstract types
    If the type annotations in the code are confusing or distracting,
    you can ignore them (just as the Python interpreter does),
    but in many cases they serve
    `as additional documentation <https://jeffrey.goldmark.org/post/what-python-doesnt-teach/#sec-types>`__
    for functions and methods.
    The more abstract types, such as using
    :py:class:`collections.abc.Mapping` instead of
    :py:class:`dict`,
    are often used to be
    `mindful of mutability <https://jeffrey.goldmark.org/post/what-python-doesnt-teach/#mindfulness-about-mutability>`__.


4. “``1 << n``” instead of “``2 ** n``”.
    You don't need to know why ``1 << n`` computes the same value
    as ``2 ** n`` or why\ [#shift]_ I am using the more obscure form; just
    know that ``1 << n`` means :math:`2^n`.

    Note, however, that these assocate differently

    .. doctest::

        >>> 2 ** 5 - 1  # (2^5) - 1
        31
        >>> 1 << 5 - 1  # 2^(5 - 1)
        16

    So when in doubt use parenthesis.

    
.. rubric:: Footnotes

.. [#expressive] Well at least “more expressive” to those familiar with the construction.

.. [#shift] The relevant difference is that ``1 << n``
    enforces the requirement that ``n`` is a non-negative integer
    while ``2 ** n`` does not
    and so the result is guaranteed to be an integer.
    I want both that enforcement and inference in those
    cases I use this mechanism to create a power of two.


