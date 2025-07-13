.. include:: /../common/unsafe.rst

.. currentmodule:: toy_crypto

*************
Motiviation
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

Nearly everyone I know with a math background complains about two things when they first learn a (typical) programmming language.
The first is that ``=`` is an assignment
instead of just a statement of eqaulity.
The second is when they discover that something of type ``int``
is strictly limited in size and is not actually an Integer.
Python solves this latter problem,
and more importanlty makes it easy to present code that deals with
larger integers.

I had previously attempted to use Golang to illustrate algorithms,
but found that the clutter of
`big.NewInt() <https://pkg.go.dev/math/big@go1.24.5#NewInt>`__ was just distracting.

And Python is terrible
======================

Python is not well-suited for secure cryptographic implementations,
which is why things like pyca_ are mostly written in C or Rust.
Effiency and defense against many side challenges require direct manipultation
of bytes and integer types that are closer to the machine.
Python, by design, does not offer direct access to memory management or low level data types.
This design helps Python be as readable as it is, but it does have consequence for cyrptographic implementations.
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
- :mod:`.ec` originated becasue I wanted to illustrate the “double and add” algorithm for scaler multiplication of a point.
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
(because I didn't know at the time that pip could install packages from a public git respositor.)

That was then. This is now
---------------------------

I do believe that what is here can be genuinely useful,
particularly for those teaching or learning about some
aspects of cyrptography.
The :mod:`.sec_games` module is not
something I've seen elsewhere and provides a mechanism for
teaching about *Modern* Cryptography.
The :mod:`.birthday` modules provides ways to calculate things that
people working with or adjacent to Cryptography might want to calculate.

