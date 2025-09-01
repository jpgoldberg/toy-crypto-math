.. include:: /../common/unsafe.rst

.. _Wycheproof repository: https://github.com/C2SP/wycheproof/
.. _Wycheproof README: https://github.com/C2SP/wycheproof/blob/main/README.md
.. _Wycheproof documentation: https://github.com/C2SP/wycheproof/blob/main/doc/index.md
.. _PyCryptodome: https://www.pycryptodome.org


Wycheproof
=================

.. py:module:: toy_crypto.wycheproof
    :synopsis: Utilities for loading and using Wycheproof project data

    This module is imported with:

        import toy_crypto.wycheproof

.. currentmodule:: toy_crypto.wycheproof

Before you jump to :doc:`usage`, first look at
:ref:`sec-wycheproof-obtain` and :ref:`sec_wycheproof_data_overview`
below.

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
I did not find such tools, so I made do with what I could do.

Ugly solutions
---------------------

At almost every step of the way with what I built for this module
I felt that there must be a better approach.
There really should be a more natural way to do what I did,
but I failed to find or construct those better ways.
Never-the-less it seems to work and the API isn't terrible. 

.. _sec-wycheproof-obtain:

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

.. _sec_wycheproof_data_overview:

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
    :open:

    .. code-block:: json
        :caption: Sample of "testvectors_v1/aes_gcm_siv_test.json"
        :name: siv.json
        :force:

        {
            "algorithm" : "AES-GCM-SIV",
            ...,
            "testGroups" : [ {
                "ivSize" : 96,
                "keySize" : 128,
                ...,
                "tests" : [
                    {
                        "tcId" : 1,
                        "comment" : "RFC 8452",
                        "flags" : [ "Ktv" ],
                        "key" : "01000000000000000000000000000000",
                        "iv" : "030000000000000000000000",
                        ...,
                        "result" : "valid"
                    }, ...
                ], ...
            ]
        }

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

.. code-block:: json
    :force:
    :caption: Sample test group from "rsa_oaep_2048_sha1_mgf1sha1_test.json"
    :name: rsa-group.json

        "testGroups" : [
            {
                "keySize" : 2048,
                "sha" : "SHA-1",
                "mgf" : "MGF1",
                "mgfSha" : "SHA-1",
                "privateKey" : {
                    "privateExponent" : ...,
                    "publicExponent" : "010001",
                    "prime1" : ...,
                    ...
                },
                "privateKeyPkcs8" : ...,
                "privateKeyPem" : ...,
                "privateKeyJwk" : ...,
                ...
                "tests" : [ ... ]
            }
        ]


:attr:`TestGroup.tests` is an an :class:`~collections.abc.Iterable` of :class:`TestCase`\s,
:attr:`TestGroup.type` is the given type of the test group,
and 
:attr:`TestGroup.other_data` is a dictionary giving access to
all other things in the test group.


Test cases
----------

All test cases in the Wycheproof data have the members

:attr:`TestCase.tcId` (JSON keyword: ``"tcID"``)
    The test case Id

:attr:`TestCase.result` (JSON keyword: ``"result"``)
    The result, which is one of "valid" or "invalid" or "acceptable",

:attr:`TestCase.flags` (JSON keyword: ``"flags"``)
    The set of flags for the case. May be the empty set.

:attr:`TestCase.comment` (JSON keyword: ``"flags"``)
    The comment. May be the empty string.

Each test case will be also have a dictionary of other elements,
specific to the particular test data.
That dictionary is available as :attr:`TestCase.other_data`.

.. code-block:: json
    :force:
    :caption: Sample test case from "primality_test.json"
    :name: prime-test.json

    "tests": [
        ...,
        {
            "tcId" : 31,
            "comment" : "counter example Axiom",
            "flags" : [
                "Pinch93",
                "CarmichaelNumber"
            ],
            "value" : "085270bd76a142abc3037d1aab3b",
            "result" : "invalid"
        }, ...
    ]

Table of contents
++++++++++++++++++

.. toctree::
    :name: wycheprooftoc
    :caption: Wycheproof
    :maxdepth: 2

    Overview <self>
    usage
    api