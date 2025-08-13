"""Loading and parsing Wycheproof test data.

Assumes you have a local copy, clone (submodule) of
https://github.com/C2SP/wycheproof

Adapted from https://appsec.guide/docs/crypto/wycheproof/wycheproo_example/
"""

from collections.abc import Mapping, Set
import os
from pathlib import Path
from importlib.resources import files, as_file
from importlib.resources.abc import Traversable
import json
import typing

from jsonschema.protocols import Validator
from referencing import Resource, Registry

type WyVector = dict[str, object]


# This is from pyca ... test/utils.py
# But I have my own comments and docs
class WycheproofTest:
    """An individual test"""

    def __init__(
        self,
        testfiledata: Mapping[str, object],
        testgroup: Mapping[str, object],
        testcase: Mapping[str, object],
    ) -> None:
        """Takes subsets of the object created from the loaded JSON.

        :param testfiledata: Test file data without the TestGroups.
        :param textgroup: TestGroup, without the tests.
        :param testcase: Individual test from the testgroup of the testfile
        """

        self.testfiledata = testfiledata
        self.testgroup = testgroup
        self.testcase = testcase

    # Today I learned that "!r" means use the __repr__, not the __str__.
    def __repr__(self) -> str:
        return "<WycheproofTest({!r}, {!r}, {!r}, tcId={})>".format(
            self.testfiledata,
            self.testgroup,
            self.testcase,
            self.testcase["tcId"],
        )

    @property
    def valid(self) -> bool:
        return self.testcase["result"] == "valid"

    @property
    def acceptable(self) -> bool:
        return self.testcase["result"] == "acceptable"

    @property
    def invalid(self) -> bool:
        return self.testcase["result"] == "invalid"

    def has_flag(self, flag: str) -> bool:
        flags = self.testcase["flags"]
        assert isinstance(flags, list)
        return flag in flags

    @typing.no_type_check
    def cache_value_to_group(self, cache_key: str, func):
        cache_val = self.testgroup.get(cache_key)
        if cache_val is not None:
            return cache_val
        self.testgroup[cache_key] = cache_val = func()
        return cache_val


class Loader:
    """Tools for loading Wycheproof test vectors."""

    def __init__(self, path: Path | None = None) -> None:
        self.local_wyche: Path
        self.schemata_dir: Path
        self.registry: Registry

        if path is None:
            r_path: Traversable = files("toy_crypto").joinpath("resources")
            if not r_path.is_dir():
                raise Exception("resource directory isn't where it should be")

            wt: Traversable = r_path.joinpath("wycheproof")
            with as_file(wt) as wp:
                self.local_wyche = wp
            if not self.local_wyche.is_dir():
                raise Exception(
                    "wycheproof directory is not where it should be"
                )

        elif isinstance(path, Path):
            self.local_wyche = path
            if not self.local_wyche.is_dir():
                raise NotADirectoryError(
                    f"'{path}' is not a directory or could not be found"
                )
        else:
            raise NotImplementedError("please respect type annotations")

        self.schemata_dir = self.local_wyche / "schemas"
        if not self.schemata_dir.is_dir():
            raise NotADirectoryError("Couldn't find 'schemas' directory")

        self.registry = Registry(retrieve=self.retrieve_from_fs)  # type: ignore[call-arg]

    @classmethod
    def collect_bigint_attrs(
        cls,
        node: object,
        attr: str = "",
    ) -> set[str]:
        """Collects attributes in schema that are "format": "BigInt".

        :param node:
            object returned by something like ``json.load()``,
            or a node within such an object in the recursive calls.
        :param attr: is the name of the current object

        Wycheproof schemata use ``{"type": "string", "format": "BigInt"}``
        for attributes that are hexadecimal strings to be converted to int.
        We need to collect the names of such attributes.

        .. note::

            There must be a more natural way use scheme annotations
            to help us process objects imported from JSON.
            But if there is, I have not yet found it.
        """

        acc: set[str] = set()

        if isinstance(node, dict):
            if node.get("format") == "BigInt" and node.get("type") == "string":
                acc.add(attr)
                return acc
            for key, value in node.items():
                acc |= cls.collect_bigint_attrs(value, key)

        elif isinstance(node, list):
            for n in node:
                acc |= cls.collect_bigint_attrs(n, "")
        return acc

    @staticmethod
    def dot_dir() -> Path:
        """The Path of the directory of the file from which this is called."""
        return Path(os.path.dirname(__file__))

    def retrieve_from_fs(self, directory: str = "") -> Resource:
        """Argument must be a str for reasons."""

        contents = json.loads(self.schemata_dir.read_text())
        return Resource.from_contents(contents)

    def load_vectors(
        self,
        path: Path | str,
    ) -> list[WyVector]:
        """Load Wycheproof test vectors.

        :param path: relative path to json file with test vectors.

        """

        path = self.local_wyche / path

        testVectors: list[WyVector] = []

        # We want to find the path to the schema from the path
        stem_name = path.stem
        scheme_file_name = stem_name + "_schema" + ".json"
        scheme_path = Path(self.schemata_dir / scheme_file_name)

        try:
            with open(scheme_path, "r") as s:
                scheme = json.load(s)
        except Exception as e:
            raise Exception(f"failed to load schema: {e}")

        try:
            with open(path, "r") as f:
                wycheproof_json = json.loads(f.read())
        except Exception as e:
            raise Exception(f"failed to load JSON: {e}")

        validator = Validator(
            schema=scheme,
            registry=self.registry,
        )  # type: ignore[misc]
        try:
            validator.validate(wycheproof_json)
        except Exception as e:
            raise Exception(f"JSON validation failed: {e}")

        convert_attr = self.collect_bigint_attrs(scheme)
        for testGroup in wycheproof_json["testGroups"]:
            for tv in testGroup["tests"]:
                for attr in convert_attr:
                    if attr in tv:
                        tv[attr] = bytes.fromhex(tv[attr])
                testVectors.append(tv)
        return testVectors

    def load_json(
        self,
        path: Path | str,
    ) -> tuple[dict[str, object], Set[str]]:
        """Returns the file data and set of properties that are BigInt format.

        :param path: relative path to json file with test vectors.

        Raises exceptions if the expected directories and files aren't
        found or can't be read.

        Raises exception of file doesn't conform to JSON Schema.
        """

        path = self.local_wyche / path

        # We want to find the path to the schema from the path
        stem_name = path.stem
        scheme_file_name = stem_name + "_schema" + ".json"
        scheme_path = Path(self.schemata_dir / scheme_file_name)

        try:
            with open(scheme_path, "r") as s:
                scheme = json.load(s)
        except Exception as e:
            raise Exception(f"failed to load schema: {e}")

        try:
            with open(path, "r") as f:
                wycheproof_json = json.loads(f.read())
        except Exception as e:
            raise Exception(f"failed to load JSON: {e}")

        validator = Validator(
            schema=scheme,
            registry=self.registry,
        )  # type: ignore[misc]
        try:
            validator.validate(wycheproof_json)
        except Exception as e:
            raise Exception(f"JSON validation failed: {e}")

        big_int_properties = self.collect_bigint_attrs(scheme)
        return wycheproof_json, big_int_properties

    def tests(
        self, path: str | Path
    ) -> typing.Generator[WycheproofTest, None, None]:
        data, big_int_properties = self.load_json(path)
        for group in data.pop("testGroups"):  # type: ignore
            cases: dict[str, object] = group.pop("tests")
            for c in cases:
                assert isinstance(c, dict)
                for property in big_int_properties:
                    if property in c:
                        c[property] = bytes.fromhex(c[property])
                yield WycheproofTest(data, group, c)
