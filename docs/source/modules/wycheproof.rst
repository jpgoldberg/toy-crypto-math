.. include:: /../common/unsafe.rst

.. _Wycheproof repository: https://github.com/C2SP/wycheproof/
.. _Wycheproof README: https://github.com/C2SP/wycheproof/blob/main/README.md
.. _Wycheproof documentation: https://github.com/C2SP/wycheproof/blob/main/doc/index.md


Wycheproof
=================

.. py:module:: toy_crypto.wycheproof
    :synopsis: Utilities for loading and using Wycheproof project data

    This module is imported with:

        import toy_crypto.wycheproof

.. currentmodule:: toy_crypto.wycheproof

What is the Wycheproof Project?
+++++++++++++++++++++++++++++++

From the Wycheproof project `Wycheproof README`_:

    Project Wycheproof is a
    `community managed <https://github.com/C2SP>`_ repository of test vectors
    that can be used by cryptography library developers to test against
    known attacks, specification inconsistencies,
    and other various implementation bugs.

    Test vectors are maintained as JSON test vector data,
    with accompanying JSON schema files
    that document the structure of the test vector data.

More detail is in that `README <Wycheproof README_>`_ file
and in the `Wycheproof documentation`_.

Why does my module exist?
++++++++++++++++++++++++++

When I first created :class:`toy_crypto.rsa.Oaep`,
I wanted to check to see whether I did so correctly,
and so testing against Wycheproof RSA OAEP test data
seemed like the best approach.

.. note::
    
    Implementating it "correctly" for my purposes does not mean that it is a secure implementation. It is not.

I had incorrectly assumed that there would be tooling
available to do that for running tests in Python.
So I hacked togther a special case for the tests I wanted to use,
lifting heavily from the tools used internally by pyca_.
While that helped me spot a bug in my implemenation (tcID 19),
there were two things about it were unsatisfying.

First of all, it was hard to generalize without taking on board all
of the pyca_ testing framework. Sure, their testing framework is better than
mine, but I wasn't ready to restructure so many of my tests.

The second annoyance is that they manually determine which which values in the
test data need to be converted from hex strings to integers or bytes.
That information is in the JSON schema assocatied with each JSON test data file.
I assumed there would be established techneques to use that information to
automate the necessary data conversions.
I did not find such tools, so I eventually rolled my own.

Ugly solutions
---------------------

At almost every step of the way with what I built for this module
I felt that there must be a better approach.
There really should be a more natural way to do what I did,
but I failed to find or construct those better ways.
Never-the-less it seems to work and the API isn't terrible. 

Obtaining the Wycheproof data
++++++++++++++++++++++++++++++

This module does not include the Wychoproof data itself;
the user needs to have a copy available to them on their own device.
The data is available from the `Wycheproof repository`_.

The portions of that repository that are necessary are the
``testvectors_v1`` directory and its contents,
the `schemas` directory and its contents,
and,
if you wish to use older test data,
the ``testvectors`` folder and its contents.

For my examples, I will assume that you have copied, cloned, or created
a submodule in `tests/resources/wycheproof`.
One way to do that would be (if your project is under git)
would doing this from within yours ``tests/`` directory.

.. prompt:: bash

    mkdir -p resources
    cd resources
    git submodule add https://github.com/C2SP/wycheproof

If your project is not under git, you could use ``git clone`` instead of ``git submodule add``.

.. note::

    I am confident that there are simply ways to do this for those who 
    aren't in a Unix-like command environment or do not use ``git`` at
    all, but I can't advise on what those ways are.

Assuming you have done so, you should have a tests directory structue something like::


    tests
    ├── __init__.py
    ├── resources
    │   └── wycheproof
    ...
            ├── schemas
    │       │   ├── aead_test_schema_v1.json
    ...
    │       ├── testvectors
    │       │   ├── aead_aes_siv_cmac_test.json
    ...
            |── testvectors_v1
    │       │   ├── a128cbc_hs256_test.json
    ...
    ├── test_this.py
    ├── test_that.py
    ├── test_other_thing.py
    ...

you could have something like this is the ``__init__.py`` file in
your ``tests`` that would make the Wycheproof resources available to
all of your test files:

.. code-block:: python
    :caption: tests/__init__.py

    import os
    from pathlib import Path
    from toy_crypto import wycheproof

    WP_ROOT = Path(os.path.dirname(__file__)) / "resources" / "wycheproof"

Loading
++++++++

To be able to load a Wycheproof JSON data file a loader must first be set up.
This not only tells the loader where the individual files are,
but it also wires in some mechanisms for loading the the various schemata
used for validating the loaded JSON.
So ideally this should only be called once.

.. testsetup::

    # Use the str BASE_TEST_DATA from doctest_global_setup

    from pathlib import Path

    WP_ROOT = Path(BASE_TEST_DATA) / "resources" / "wycheproof"
    assert WP_ROOT.is_dir(), str(WP_ROOT)

Assuming that you have something like ``WP_ROOT`` set up,
you can set up the test loader by intializing a :class:`Loader`.

.. doctest::
    from pathlib import Path
    # WP_ROOT: Path = ... # set up elsewhere
    loader = wycheproof.Loader(WP_ROOT)

Now we can load some test data.


.. autoclass:: Loader
    :members:


