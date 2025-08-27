.. include:: /../common/unsafe.rst

.. _PyCryptodome: https://www.pycryptodome.org


Usage
=================

.. currentmodule:: toy_crypto.wycheproof

This document walks through a concrete example.
It assumes that you have
obtained the wcyhoproof data as discussed in
:ref:`sec-wycheproof-obtain`,
and that you have at least glanced the
:ref:`data overview section <sec_wycheproof_data_overview>`.


Structure of use
+++++++++++++++++

The structure of one way to use this module might look something like

.. code-block:: python

    import toy_crypto.wycheproof
    # import ... # the modules with the things you will be testing

    # WP_ROOT: Path = ... # a pathlib.Path for the root wycheproof directory
    loader = wycheproof.Loader(WP_ROOT)  # This only needs to be done once
    ...

    # Get test data from one of the data files

    test_data = loader.load("SOME_WYCHEPROOF_DATA_FILE_test.json")
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

An example
+++++++++++

We will be testing RSA decryption from PyCryptodome_
against the Wycheproof OAEP test data for 2048-bit keys with SHA1 as the
hash algrorithm and MGF1SHA1 as the mask generation function.
The data file for those tests is in
``testvectors_v1/rsa_oaep_2048_sha1_mgf1sha1_test.json`` relative to WP_ROOT.

In what follows, we assume that you have already set up ``WP_ROOT``
as a :py:class:`pathlib.Path` with the appropriate file system location.
See :ref:`sec-wycheproof-obtain` for discusson of ways to do that.

Set up loader
--------------

.. testsetup:: 

    # Use the str BASE_TEST_DATA from doctest_global_setup

    from pathlib import Path

    WP_ROOT = Path(BASE_TEST_DATA) / "resources" / "wycheproof"
    assert WP_ROOT.is_dir(), str(WP_ROOT)


This assumes that you have already set up ``WP_ROOT``
(or whatever you wish to call it)
as a :py:class:`pathlib.Path` with the appropriate file system location
as discussed :ref:`sec-wycheproof-obtain`.

To be able to load a wycheproof JSON data file a loader must first be set up.
The :class:`Loader`` you create will not only know where the data files are,
but it will have internal mechanisms set up for constructing the schemata
used for validating the loaded JSON.

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

Now what we have ``loader``, we can use it
to load Wycheproof data.

The data is loaded using :meth:`Loader.load`.
The loaded :class:`TestData` instance is not the
raw result of loading JSON, but many of its internals
still reflect its origins.

..  testcode::
   
    test_data = loader.load("rsa_oaep_2048_sha1_mgf1sha1_test.json")

    assert test_data.header == "Test vectors of type RsaOeapDecrypt check decryption with OAEP."

For each :class:`TestGroup`
-----------------------------------

Test cases are organized into test groups within the raw data.
See :ref:`sec_wycheproof_data_overview` for more information about
what kinds of things are typically found in test groups.
:attr:`TestData.groups` returns an 
Iterator of :class:`TestGroup\s`.

In the case of this test data each
:class:`TestGroup` specifies
the parameters needed to construct a private RSA key
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
In this example,
I will use the :external+crypto:func:`Crypto.PublicKey.RSA.import_key` method
to get the key information from the PEM format.


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
        

For each :class:`TestCase`
--------------------------------------

We are finally ready for our actual tests.

In addition to the properties that all Wycheproof test cases have,
the test cases here have. 

"msg"
    The plaintext message

"ct"
    The ciphertext

"label"
    The OAEP label that is rarely ever used.

These are accesible as keys to the dictionary
:attr:`TestCase.other_data`.

Fortunately the defaults for creating a cryptor,
:external+crypto:func:`Crypto.Cipher.PKCS1_OAEP.new`
cryptor with PyCryptodome_
uses as hash algoririthm, mask generation function are the ones we
are testing here, so we won't have to specify them.
We can create the cryptor we wish to test with

.. code-block:: python

    cryptor = PKCS1_OAEP.new(key = sk, label = label)

where ``sk`` is the private key we set up for the test group,
and ``label`` is from each test.

..  testcode::

    test_count = 0
    for g, sk in group_pairs:
        for case in g.tests:
            test_count += 1
        
            label = case.other_data["label"]
            ciphertext = case.other_data["ct"]
            message = case.other_data["msg"]

            cryptor = PKCS1_OAEP.new(key=sk, label=label)

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
