"""Loading and parsing Wycheproof test data.

Assumes you have a local copy, clone (submodule) of
https://github.com/C2SP/wycheproof

Adapted from https://appsec.guide/docs/crypto/wycheproof/wycheproo_example/
"""

from collections.abc import Generator, Mapping, Set
from copy import copy, deepcopy
from pathlib import Path
import json
import typing

from jsonschema.protocols import Validator
from referencing import Resource, Registry

# I wouldn't need to have a whole bunch of isinstance instances
# if I could use the schema to flesh out types. But, alas,
# I have not figured out a way to do that reasonably.

type StrDict = dict[str, object]


def deserialize_top_level(
    properties: StrDict, formats: Mapping[str, str]
) -> None:
    """Mutates. Deserializes root level members according for format

    Any string values in ``HexBytes`` format
    is converted to :py:class:`bytes`,
    and any in ``BigInt`` format
    is converted to an signed :py:class:`int`.
    """

    for p, s in properties.items():
        if not isinstance(s, str):
            continue

        match formats.get(p):
            case None:
                pass
            case "HexBytes":
                properties[p] = bytes.fromhex(s)
            case "BigInt":
                properties[p] = int.from_bytes(
                    bytes.fromhex(s), byteorder="big", signed=True
                )
            case "Asn" | "Jwk" | "Pem" | "Der":
                # Leave as string, as it might be invalid
                pass
            case _:
                # TODO: Should warn of unknown format
                pass


class TestCase:
    def __init__(self, test_case: Mapping[str, object]) -> None:
        # We are going to modify data by popping, so we will copy things.
        # A shallow copy should be enough
        data = dict(copy(test_case))

        tcId = data.pop("tcId", None)
        if tcId is None:
            raise ValueError('Missing "tcId" key')
        self._tcId: int = int(tcId)

        result = data.pop("result", None)
        if not isinstance(result, str):
            raise ValueError('Missing or garbled "result"')

        if result not in ("valid", "invalid", "acceptable"):
            raise ValueError("Weird result status")
        self._result: str = result

        self._comment: str = data.pop("comment", "")  # type: ignore[assignment]
        flags: list[str] = data.pop("flags", [])  # type: ignore[assignment]
        self._flags: Set[str] = set(flags)

        self._data = data

    def __getitem__(self, key: str) -> object:
        return self._data[key]

    @property
    def tcId(self) -> int:
        return self._tcId

    @property
    def result(self) -> str:
        return self._result

    @property
    def valid(self) -> bool:
        return self._result == "valid"

    @property
    def acceptable(self) -> bool:
        return self._result == "acceptable"

    @property
    def invalid(self) -> bool:
        return self._result == "invalid"

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def flags(self) -> Set[str]:
        return self._flags

    def has_flag(self, flag: str) -> bool:
        return flag in self._flags

    def __repr__(self) -> str:
        s = f"tcId: {self.tcId}"
        if self.comment != "":
            s += f" ({self.comment})"
        s += f"; {self._result}"
        flag_repr = f"{repr(self.flags)}" if self.flags else "None"
        s += f"; flags: {flag_repr}"
        s += f"; other: {repr(self._data)}"

        return s


class TestGroup:
    def __init__(
        self, group: dict[str, object], formats: Mapping[str, str]
    ) -> None:
        self._formats = formats
        self.group: dict[str, object] = copy(group)

        deserialize_top_level(self.group, formats)

        tests: list[dict[str, object]]

        try:
            tests = self.group.pop("tests")  # type: ignore[assignment]
        except KeyError:
            raise ValueError('Group must have "tests')
        assert isinstance(tests, list)
        self._tests: list[dict[str, object]] = tests

    def __getitem__(self, key: str) -> object:
        return self.group[key]

    @property
    def tests(self) -> Generator[TestCase]:
        for t in self._tests:
            deserialize_top_level(t, self._formats)
            yield TestCase(t)


class Data:
    """The Python object that results from loading the JSON source."""

    def __init__(
        self, data: dict[str, object], formats: Mapping[str, str]
    ) -> None:
        self._formats = formats
        _data: dict[str, object] = deepcopy(data)
        groups = _data.pop("testGroups", None)
        if groups is None:
            raise ValueError('There should be a "testGroups" key in the data')
        assert isinstance(groups, list)
        self._groups: list[dict[str, object]] = groups

        header: list[str] = _data.pop("header", "")  # type: ignore[assignment]

        # Hungarian Notation (well, it would be vonálHeader)
        vonal_header: str = " ".join(header)
        assert isinstance(vonal_header, str)
        self._header: str = vonal_header

        alg = _data.pop("algorithm", "")
        assert isinstance(alg, str)
        self._algorithm: str = alg

        self._data: dict[str, object] = _data

    @property
    def header(self) -> str:
        return self._header

    @property
    def groups(self) -> Generator[TestGroup]:
        for g in self._groups:
            yield TestGroup(g, self._formats)

    @property
    def algorithm(self) -> str:
        return self._algorithm

    @property
    def data(self) -> Mapping[str, object]:
        return self._data


# This is from pyca ... test/utils.py
# But I have my own comments and docs
class Test:
    """An individual test with a useful representation."""

    def __init__(
        self,
        data: Mapping[str, object],
        group: Mapping[str, object],
        case: Mapping[str, object],
    ) -> None:
        """Takes subsets of the object created from the loaded JSON.

        To conduct a test, we only need the ``.cases`` attribute,
        but ``.data`` and ``.group`` are useful for describing the case.

        :param data: Test file data without the TestGroups.
        :param group: TestGroup, without the tests.
        :param case: Individual test from the group
        """

        self.data = data
        self.group = group
        self.case = case

    def __repr__(self) -> str:
        return "<WycheproofTest({!r}, {!r}, {!r}, tcId={})>".format(
            self.data,
            self.group,
            self.case,
            self.case["tcId"],
        )

    @property
    def valid(self) -> bool:
        return self.case["result"] == "valid"

    @property
    def acceptable(self) -> bool:
        return self.case["result"] == "acceptable"

    @property
    def invalid(self) -> bool:
        return self.case["result"] == "invalid"

    def has_flag(self, flag: str) -> bool:
        flags = self.case["flags"]
        assert isinstance(flags, list)
        return flag in flags

    # Copied from pyca. I do not know what this is for
    @typing.no_type_check
    def cache_value_to_group(self, cache_key: str, func):
        cache_val = self.group.get(cache_key)
        if cache_val is not None:
            return cache_val
        self.group[cache_key] = cache_val = func()
        return cache_val


class Loader:
    """Tools for loading Wycheproof test vectors."""

    def __init__(self, path: Path) -> None:
        """Establishes wycheproof data directory and preregisters schemata.

        :param path:
            Path of wycheproof root.

        Unless you have multiple locations with Wycheproof-like test data,
        you really should just call this constructor once.
        """

        self._root_dir: Path
        self._schemata_dir: Path
        self.registry: Registry

        self._root_dir = path
        if not self._root_dir.is_dir():
            raise NotADirectoryError(
                f"'{path}' is not a directory or could not be found"
            )

        self._schemata_dir = self._root_dir / "schemas"
        if not self._schemata_dir.is_dir():
            raise NotADirectoryError("Couldn't find 'schemas' directory")

        self.registry = Registry(
            retrieve=self.retrieve_from_dir,  # type: ignore[call-arg]
        )

    @property
    def root_dir(self) -> Path:
        return self._root_dir

    @classmethod
    def collect_formats(cls, schema: dict[str, object]) -> Mapping[str, str]:
        """Collects format annotation for all string types in schema.

        :param schema: The to collect string format annotations from.

        .. warning::

            If the same property name is used in different parts of the schema
            and have distinct formats, which format will be assigned to the
            single property name is undefined.
        """

        return cls._collect_formats(schema, property="")

    @classmethod
    def _collect_formats(
        cls, node: object, property: str = ""
    ) -> dict[str, str]:
        # There really must be tools to match data properties with schemata,
        # but I can't find any.

        local_dict: dict[str, str] = {}

        if isinstance(node, dict):
            # Base of recursion
            format = node.get("format")
            if format is not None:
                assert isinstance(format, str)
                return {property: format}

            # Recurse through dictionary values
            for key, value in node.items():
                local_dict.update(cls._collect_formats(value, key))

        elif isinstance(node, list):
            # Recurse through list members
            # (Do schemata even have lists?)
            for n in node:
                local_dict.update(cls._collect_formats(n, ""))
        return local_dict

    # https://python-jsonschema.readthedocs.io/en/stable/referencing/#resolving-references-from-the-file-system
    def retrieve_from_dir(self, directory: str = "") -> Resource:
        """Retrieves schema from file system directory.
        Retrieval function to be passed to Registry.

        :param directory:
            A string representing the file system directory
            from which schemata are retrieved.
        """

        contents = json.loads(self._schemata_dir.read_text())
        return Resource.from_contents(contents)

    def load_json(
        self,
        path: Path | str,
        *,
        subdir: str = "testvectors",
    ) -> Data:
        """Returns the file data and dictionary of property formats

        :param path: relative path to json file with test vectors.

        Raises exceptions if the expected directories and files aren't
        found or can't be read.

        Raises exception of file doesn't conform to JSON Schema.
        """
        path = self._root_dir / subdir / path

        try:
            with open(path, "r") as f:
                wycheproof_json = json.loads(f.read())
        except Exception as e:
            raise Exception(f"failed to load JSON: {e}")

        scheme_file = wycheproof_json["schema"]
        scheme_path = Path(self._schemata_dir / scheme_file)

        try:
            with open(scheme_path, "r") as s:
                scheme = json.load(s)
        except Exception as e:
            raise Exception(f"failed to load schema: {e}")

        validator = Validator(
            schema=scheme,
            registry=self.registry,
        )  # type: ignore[misc]
        try:
            validator.validate(wycheproof_json)
        except Exception as e:
            raise Exception(f"JSON validation failed: {e}")

        formats = self.collect_formats(scheme)
        return Data(wycheproof_json, formats)
