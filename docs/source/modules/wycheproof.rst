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

    WP_ROOT = Path(os.path.dirname(__file__)) / "resources" / "wycheproof"

Data overview
+++++++++++++

To be able to use Wycheproof data for any specific set of tests,
you will need to know what is in is in the data and how it structured.

Each data file has a name like ``*_test.json``.
Those JSON files all contain a key ``"testGroups"``,
and each test group has a JSON key ``"tests"``

The following :ref:`JSON sample <siv.json>` contains a small portion of what you might see
in a wycheproof JSON test data file.

.. collapse:: Exerpt of test JSON file

    .. code-block:: json
        :caption: Sample of "testvectors_v1/aes_gcm_siv_test.json"
        :name: siv.json

        {  "algorithm" : "AES-GCM-SIV",
            "testGroups" : [ {
                "ivSize" : 96,
                "keySize" : 128,
                "tagSize" : 128,
                "type" : "AeadTest",
                "tests" : [
                    {
                    "tcId" : 1,
                    "comment" : "RFC 8452",
                    "flags" : [ "Ktv" ],
                    "key" : "01000000000000000000000000000000",
                    "iv" : "030000000000000000000000",
                    "aad" : "",
                    "msg" : "",
                    "ct" : "",
                    "tag" : "dc20e2d83f25705bb49e439eca56de25",
                    "result" : "valid"
                    } ... ] ] ... }

The user will need to check for themselves what sorts data
are in each test group and in each test. 

:func:`Loader.load` loads a and returns a :class:`TestData` object.
:attr:`TestData.groups` is an
:class:`~collections.abc.Iterable` of :class:`TestGroup` instances.

Test groups
------------

Each test group typically contains information for constructing keys or data
that will be used for all all of the tests within the group.
They typically provide equivalent keys in multiple formats.

.. code-block::

    {"testGroups" : [ {
        "keySize" : 2048,
        "sha" : "SHA-1",
        "mgf" : "MGF1",
        "mgfSha" : "SHA-1",
        "privateKey" : {
        "modulus" : ...,
        "privateExponent" : ...,
        "publicExponent" : "010001",
        "prime1" : ...,
        "prime2" : ...,
        ...
        },
        "privateKeyPkcs8" : ...,
        "privateKeyPem" : ...,
        "privateKeyJwk" : { ... },
        "tests" : [ ... ]
    } ] }



:attr:`TestGroup.tests` is an an :class:`~collections.abc.Iterable` of :class:`TestCase` instances. All test cases in the Wycheproof data have

:attr:`TestCase.tcId`
    The test case Id

:attr:`TestCase.result`
    The result, which is one of "valid" or "invalid" or "acceptable",

:attr:`TestCase.flags`
    The set of flags for the case. May be the empty set.

:attr:`TestCase.comment`
    The comment. May be the empty string.

Each test case will be also have a dictionary of other elements,
specific to the particular test data.
This dictionary is available as :attr:`TestCase.fields`.

Usage
+++++++++++++


The structure of one way to use this might look something like

.. code-block:: python

    # WP_ROOT: Path = ... # a pathlib.Path for the root wycheproof directory
    loader = wycheproof.Loader(WP_ROOT)  # This only needs to be done once
    ...

    # Get test data from one of the data files

    test_data = loader.load("SOME_DATA_FILE_test.json")
    ... # May wish to get some information from test_data
        # for loggging or reporting.

    for group in test_.groups:
        ... # Per TestGroup setup
        for test in group.tests:
            ... # set up for specific test
            ... # perform computation with thing you are testing
            ... # Check that your results meet expectations

For the example below, we will step through parts of that,
but will sometimes need to use a different flow so that each
of the parts actually runs when contructing this document.

We will be testing RSA decryption from ``pycryptodome``
passes tests for a 2048-bit key with SHA1 as the
hash algrorithm and MGF1SHA1 as the mask generation function.
The data file for those tests is in ``testvectors_v1/rsa_oaep_2048_sha1_mgf1sha1_test.json`` relative to WP_ROOT.

In what follows, we assume that you have already set up ``WP_ROOT`` as a :py:class:`pathlib.Path` with the appropriate file system location.

.. testsetup:: 

    # Use the str BASE_TEST_DATA from doctest_global_setup

    from pathlib import Path

    WP_ROOT = Path(BASE_TEST_DATA) / "resources" / "wycheproof"
    assert WP_ROOT.is_dir(), str(WP_ROOT)

Set up loader
--------------

To be able to load a Wycheproof JSON data file a loader must first be set up.
This not only tells the loader where the individual files are,
but it also wires in some mechanisms for loading the the various schemata
used for validating the loaded JSON.
So ideally this should only be called once.

Assuming that you have something like ``WP_ROOT`` set up,
you can set up the test loader by intializing a :class:`Loader`.

..  testcode::

    from pathlib import Path
    from toy_crypto import wycheproof

    # These imports include the function we will be testing
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP

    # WP_ROOT: Path = ... # set up elsewhere
    loader = wycheproof.Loader(WP_ROOT)

Loading the test data
----------------------

The data is loaded using :meth:`Loader.load`.
The loaded :class:`TestData` instance is not the
raw result of loading JSON, but many of its internals
still reflect its origins.

..  testcode::
   
    test_data = loader.load("rsa_oaep_2048_sha1_mgf1sha1_test.json")

    assert test_data.header == "Test vectors of type RsaOeapDecrypt check decryption with OAEP."

TestGroup preparation
------------------------

Test cases are organized into "testGroups" within the raw data.
In the case of this test data each TestGroup specifies
a the parameters needed to construct a private RSA key
that is to be used for all tests in the group.
So you might normally use something like

.. code-block:: python

    for group in test_data.tests:
        ... # Per TestGroup setup
        for test in group.tests: ...

But I can't run that in a doctest, so we will instead
collect tuples of TestGroup, rsa.PrivateKey pairs.

The TestGroup data in this file includes an RSA private key
that will be used for all tests in the group.
The key is offered in several formats.
In this example, I will use the ``pycryptomdome`` RSA.import_key method
to get the key from the PEM format.


..  testcode::

    group_pairs = [
        (g, RSA.import_key(g["privateKeyPem"])) for g in test_data.groups
    ]

    ## Let's do some sanity checks on the private keys
    for _, sk in group_pairs:
        assert sk.size_in_bits() == 2048
        assert sk.has_private()

Each group also has the parameters used for our RSA decryption.
These are the same for all test groups in this particular data set.
So let's just do a sanity check on this just for demonstration purposes.

..  testcode::

    for g, _ in group_pairs:
        assert g["keySize"] == 2048
        assert g["sha"] == "SHA-1"
        assert g["mgf"] == "MGF1"
        assert g["mgfSha"] == "SHA-1"
        

Testing against each :class:`TestCase`
--------------------------------------

And now we are finally ready for our actial tests.

And all of the cases for these specific tests have a

"msg"
    The plaintext message

"ct"
    The ciphertext

"label"
    The OAEP label that is rarely ever used.

Fortunately the default for creating a cryptor with pycryptodome
uses as hash algoririthm, mask generation function are the ones we
are testing here, so we won't have to specify them.

..  testcode::

    test_count = 0
    for g, sk in group_pairs:
        for case in g.tests:
            test_count += 1
        
            label = case.fields["label"]
            ciphertext = case.fields["ct"]
            message = case.fields["msg"]

            cryptor = PKCS1_OAEP.new(
                key = sk,
                label = label,
            )

            our_message: bytes = b''
            try:
                our_message = cryptor.decrypt(ciphertext)
            except ValueError:
                assert case.invalid
            else:
                assert case.valid
                assert our_message == message

    print(f"Completed a total {test_count} tests in {len(group_pairs)} group(s).")

.. testoutput::

    Completed a total 36 tests in 1 group(s).



Classes
+++++++++

.. autoclass:: Loader
    :members:

.. autoclass:: TestCase
    :members:

.. autoclass:: TestGroup
    :members:

.. autoclass:: TestData
    :members:


