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

    from toy_crypto import wycheproof
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

If for some reason the JSON does not validate against the expected schema,
warnings will be logged at the
|WARNING|_ level.

.. |WARNING| replace:: ``logging.WARNING``
.. _WARNING: https://docs.python.org/3/library/logging.html#logging.WARNING

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

The private key is offered in several formats.
In this example,
I will use the :external+crypto:func:`Crypto.PublicKey.RSA.import_key` method
to get the key information from the PEM format.


..  testcode::

    for group in test_data.groups:
        pem = group.other_data["privateKeyPem"]
        sk = RSA.import_key(pem)

        ## Let's do some sanity checks on the private keys
    
        assert sk.size_in_bits() == 2048
        assert sk.has_private()

Each group also has the parameters used for our RSA decryption.
These are the same for all test groups in this particular data set.
So let's just do a sanity check on this just for demonstration purposes.

..  testcode::

    for g in test_data.groups:
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
    group_count = 0
    for g in test_data.groups:
        group_count += 1
        pem = group.other_data["privateKeyPem"]
        sk = RSA.import_key(pem)

        for case in g.tests:
            test_count += 1
        
            label: bytes = case.other_data["label"]
            ciphertext: bytes = case.other_data["ct"]
            message: bytes = case.other_data["msg"]

            cryptor = PKCS1_OAEP.new(key=sk, label=label)

            decrypted: bytes
            try:
                decrypted = cryptor.decrypt(ciphertext)
            except ValueError:
                assert case.invalid
            else:
                assert case.valid
                assert decrypted == message

    assert test_count == test_data.test_count
    print(f"Completed a total {test_count} tests in {group_count} group(s).")

.. testoutput::

    Completed a total 36 tests in 1 group(s).

.. _sec_wycheproof_data_conversion:

Data conversion
++++++++++++++++++++++++++++

The TLDR for this section is that you are advised to make sure that
things like ``case.other_data["ct"]`` are of the data types you expect
when you run tests.
Be familiar with the data you are importing, and do not relie
on the fully automatic conversion from hex strings to bytes or integers
to always get things right.

We will continue with the same example as above for this discussion.

In some of the test cases in the test data we used,
the ``"ct"``, ``"msg"``, and ``"label"`` JSON keywords
have values that are strings.
In all of those cases, the strings are hex encoded byte sequences.
Consider this exceprt from test case 9:

.. code-block:: json
    :force:

    {
        "tcId" : 9,
        "comment" : "",
        "flags" : [
            "EncryptionWithLabel"
        ],
        "msg" : "313233343030",  // That is actually hex encoded
        "ct" : ..., // A longer string of hex digits was here
        "label" : "000102030405060708090a0b0c0d0e0f10111213",
        "result" : "valid"
    }

But when we ran our tests we were able to use code like

.. code-block:: python

    label: bytes = case.other_data["label"]
    ciphertext: bytes = case.other_data["ct"]
    message: bytes = case.other_data["msg"]

and those things really were bytes.

The initiallizers for :class:`TestGroup` and :class:`TestCase`
automatically perform *some* necessary conversions from hexidecimal
strings to :py:class:`bytes` or :py:class:`int` as appropriate.
It does this using the data from :attr:`TestData.formats`,
which is a mapping from JSON keywords to information about how
the string is formated.

.. testcode::

    # We have already loaded test_data with:
    # test_data = loader.load("rsa_oaep_2048_sha1_mgf1sha1_test.json")

    formats: dict[str, str] = test_data.formats

    assert formats["ct"] == "HexBytes"
    assert formats["publicExponent"] == "BigInt" # Not used yet

:attr:`TestData.formats` is constructed by inspecting the schema associated with
with the JSON file requesting during loading.
That may give incorrect results when there are multiple places a particular
JSON keyword might exist in the data.
As a consequence, the automatic conversion is conservative and only
acts on the keywords in the top-most level of a test group or test case.

Additionally, the :attr:`TestData.formats` dictionary will be empty
when the loaded JSON was successfully validated when the JSON was loaded.
Users can use :func:`TestData.schema_is_valid` to check
whether the JSON test file was successfully validated
against its JSON schema.
When that validation fails, 


Semi-automatic conversion
-------------------------

As mentioned above,
the fully automatic conversation using :attr:`TestData.formats`
is only performed at the top leve of
each :class:`TestGroup` and :class:`TestCase`.

Suppose in our OAEP test, instead of creating the
private key from the PEM format in each test group
we created it through the information in ``other_data["privateKey"]``.

.. code-block:: json
    :force:

        "testGroups" : [
            {
                ...
                "privateKey" : {
                    "privateExponent" : ...,
                    "publicExponent" : "010001", // that is a hex string
                    "prime1" : ...,
                    "prime2" : ...,
                    ...
                },
                "privateKeyPem" : ...,
                ...
                "tests" : [ ... ]
            }
        ]

we might need to extract the values of
``"publicExponent"``, ``"prime1"``, and ``"prime2"``
in each test group.
But these are not top-level keys within the test group,
and so they will remain as hex strings.

.. testcode::

    # We will test for just the first group
    group = next(test_data.groups)

    priv_key_data = group.other_data["privateKey"]
    e = priv_key_data["publicExponent"]

    assert isinstance(e, str)
    print(e)

.. testoutput::

    010001

But because ``formats`` does contain information for the relevant
members of ``group.other_data["privateKey"]`` we can manually
call automatic conversion using :func:`deserialize_top_level`.
Note that this mutates the dictionary it is given.

.. testcode::

    group = next(test_data.groups)

    priv_key_data = group.other_data["privateKey"]
    
    wycheproof.deserialize_top_level(priv_key_data, test_data.formats)

    e = priv_key_data["publicExponent"]
    p = priv_key_data["prime1"]
    q = priv_key_data["prime2"]
    N = priv_key_data["modulus"]

    assert p * q == N

    assert isinstance(e, int)

    print(e)

.. testoutput::

    65537

Note again that schema loading and validation can fail


Gotchas
++++++++

Pretty much all of the many ways this can break are a consequence
of the fact that I haver not found a way to make use of JSON schemata
the way I feel they should be able to be used.
When I started working on this module, I had assumed that there
would be a fairly straigthforward way to make use of the JSON schema
loaded for each test file to reason about the loaded JSON within Python code.

Hard-coded data assmptions
--------------------------

The code here makes assumptions about things that will be common
to all of the wycheproof JSON test files. Similarly it makes assumptions
about what each test group within those files will have.
I have yet to write tests to see if those actually hold of each test file.
It is more likely that these assumptions will fail in with test vectors from the
older ``wycheproof/testvectors`` directory than in the (default) 
``wycheproof/testvectors``.

If you find that the assumptions fail for things in ``wycheproof/testvectors`` definitely let me know.

Data conversion
----------------

As discussed in :ref:`sec_wycheproof_data_conversion`
the automatic data conversion of hexidecimal strings
to :py:class:`bytes` or :py:class:`int`\s will miss things
that you will need to manually handle, perhaps with the help of
:func:`deserialize_top_level`.

Additionally there are currently (August 29, 2025)
52 test files in the wycheproof project that are missing schemas.
In these cases, no automatic conversion will be attempted
and :attr:`TestData.formats` will be empty.
:func:`TestData.schema_is_valid` can be used to check
if there was a problem during schema loading and validation.
:attr:`TestData.schema_file` can be used for further debugging.

It is also possible that it will attempt to convert things
it shouldn't or be mistaken about which conversion to use.
If you find that this occurs, please let me know.

Other data is just the left overs
----------------------------------

The dictionares
:attr:`TestData.other_data`,
:attr:`TestGroup.other_data`,
and :attr:`TestCase.other_data`
exclude things for which those classes automatically offer as properties.
For example, the existence of :attr:`TestGroup.algorithm` means that
trying something like ``test_data.other_data["algorithm"]`` will result
in a :py:class:`KeyError`.

There are reasons for my choice here.
Perhaps not good reasons, but reasons none the less.








