"""Loading and parsing Wycheproof test data.

Assumes you have a local copy, clone (submodule) of
https://github.com/C2SP/wycheproof

Adapted from https://appsec.guide/docs/crypto/wycheproof/wycheproo_example/
"""

from collections.abc import Iterator, Mapping, Sequence, Set
from copy import copy
from pathlib import Path
import json

try:
    from warnings import deprecated
except ImportError:
    from typing_extensions import deprecated

from jsonschema import validators
from referencing import Resource, Registry
from referencing.jsonschema import DRAFT202012

import jsonref  # type: ignore[import-untyped]

import logging

logging.getLogger(__name__)


def deserialize_top_level(
    properties: dict[str, object], formats: Mapping[str, str]
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
            case "Asn" | "Pem" | "Der":
                # Leave as string. Some might be deliberately invalid
                pass
            case "EcCurve" | "MdName":
                # These are meant to be strings
                pass
            case _:
                logging.info(f"'{p}' has unexpected format: {formats[p]}")
                pass


class TestCase:
    def __init__(self, test_case: Mapping[str, object]) -> None:
        # We are going to modify data by popping, so we will copy things.
        # A shallow copy should be enough
        data = dict(copy(test_case))

        tcId = data.pop("tcId", None)
        if tcId is None:
            raise ValueError('Missing "tcId" key')
        self._tcId: int = tcId  # type: ignore[assignment]

        result = data.pop("result", None)
        if not isinstance(result, str):
            raise ValueError('Missing or garbled "result"')

        if result not in ("valid", "invalid", "acceptable"):
            raise ValueError("Weird result status")
        self._result: str = result

        self._comment: str = data.pop("comment", "")  # type: ignore[assignment]
        self._flags: Set[str] = data.pop("flags", [])  # type: ignore[assignment]

        self._fields = data

    @deprecated("Use 'other_data' instead")
    def __getitem__(self, key: str) -> object:
        return self._fields[key]

    @property
    def other_data(self) -> Mapping[str, object]:
        """The test case data that isn't captured by known properties."""
        return self._fields

    @property
    def tcId(self) -> int:
        """The test case ID ``"tcId`` of the test case"""
        return self._tcId

    @property
    def result(self) -> str:
        """The expected result of the test

        Should be one of "valid", "invalid", "acceptable"
        """
        return self._result

    @property
    def valid(self) -> bool:
        """If the test case is expected to be valid."""
        return self._result == "valid"

    @property
    def acceptable(self) -> bool:
        """If the test case is expected to be acceptable."""
        return self._result == "acceptable"

    @property
    def invalid(self) -> bool:
        """If the test case expected to be invalid."""
        return self._result == "invalid"

    @property
    def comment(self) -> str:
        """The comment for the case.

        The comment might be the empty string.
        """
        return self._comment

    @property
    def flags(self) -> Set[str]:
        """The set of flags that are set for the case."""
        return self._flags

    def has_flag(self, flag: str) -> bool:
        """True if ``flag`` is set for this case."""
        return flag in self._flags

    def __repr__(self) -> str:
        """Designed for useful error messages in tests."""
        s = f"tcId: {self.tcId}"
        if self.comment != "":
            s += f" ({self.comment})"
        s += f"; {self._result}"
        flag_repr = f"{repr(self.flags)}" if self.flags else "None"
        s += f"; flags: {flag_repr}"
        s += f"; other: {repr(self._fields)}"

        return s


class Note:
    """Notes on flags for in TestData"""

    def __init__(self, note_name: str, notes: dict[str, object]) -> None:
        self._flag_name = note_name
        note = notes[self._flag_name]
        assert isinstance(note, dict)

        # common.json schema says bugType must exist
        self._bug_type: str
        bug_type = note["bugType"]
        self._bug_type = bug_type["description"]  # type: ignore[assignment]

        self._description: str | None = note.get("description", None)
        self._effect: str | None = note.get("effect", None)
        self._links: Sequence[str] = note.get("links", [])
        self._cves: Sequence[str] = note.get("cves", [])

    @property
    def bug_type(self) -> str:
        """The type of the bug tested for"""

        return self._bug_type

    @property
    def description(self) -> str | None:
        """A description of the flag"""

        return self._description

    @property
    def effect(self) -> str | None:
        """The expected effect of failing the test vector"""

        return self._effect

    @property
    def links(self) -> Sequence[str]:
        """A list of potentially related references"""

        return self._links

    @property
    def cves(self) -> Sequence[str]:
        """A list of potentially related CVEs"""

        return self._cves


class TestGroup:
    """Data that is common to all tests in the group."""

    def __init__(
        self, group: dict[str, object], formats: Mapping[str, str]
    ) -> None:
        # These will be accessed as properties
        self._data: Mapping[str, object]
        self._tests: Sequence[dict[str, object]]
        self._type: str | None

        self._formats = formats
        data: dict[str, object] = copy(group)

        try:
            self._tests = data.pop("tests")  # type: ignore[assignment]
        except KeyError:
            raise ValueError('Group must have "tests')

        self._type = data.pop("type", None)  # type: ignore[assignment]

        deserialize_top_level(data, formats)

        self._data = data

    @deprecated("Use 'other_data' instead")
    def __getitem__(self, key: str) -> object:
        return self._data[key]

    @property
    def tests(self) -> Iterator[TestCase]:
        """All of the test cases in the group."""
        for t in self._tests:
            deserialize_top_level(t, self._formats)
            yield TestCase(t)

    @property
    def type(self) -> str | None:
        """The test group type."""

        return self._type

    @property
    def other_data(self) -> Mapping[str, object]:
        """The data that isn't captured by known properties."""
        return self._data


class TestData:
    """The object that results from loading a wycheproof JSON file."""

    def __init__(
        self,
        data: dict[str, object],
        formats: Mapping[str, str],
        schema_path: Path,
        schema_status: str = "valid",
    ) -> None:
        self._formats = formats
        self._groups: Sequence[dict[str, object]]
        self._algorithm: str
        self._header: str
        self._notes: Mapping[str, Note]
        self._data: dict[str, object]
        self._test_count: int | None

        self._schema_file = schema_path

        assert schema_status in ("valid", "loaded", "not-loaded")
        self._schema_status = schema_status

        # Shallow copy should be ok, because everything we
        # pop out of this gets copied.
        _data: dict[str, object] = copy(data)

        try:
            self._groups = _data.pop("testGroups")  # type: ignore[assignment]
        except KeyError:
            raise ValueError('There should be a "testGroups" key in the data')

        self._test_count = _data.pop("numberOfTests", None)  # type: ignore[assignment]

        # docs say header can be a string as well as a list of strings
        header: list[str] | str = _data.pop("header", "")  # type: ignore[assignment]
        if not isinstance(header, str):
            header = " ".join(header)
        self._header = header

        src_notes: dict[str, dict[str, object]] = _data.get("Notes", dict())  # type: ignore[assignment]

        self._notes = {
            name: Note(name, note) for name, note in src_notes.items()
        }

        self._algorithm = _data.pop("algorithm", "")  # type: ignore[assignment]

        self._data = _data

    @property
    def header(self) -> str:
        return self._header

    @property
    def groups(self) -> Iterator[TestGroup]:
        for g in self._groups:
            yield TestGroup(g, self._formats)

    @property
    def algorithm(self) -> str:
        return self._algorithm

    @deprecated("Use 'other_data' instead")
    def __getitem__(self, key: str) -> object:
        return self._data[key]

    @property
    def other_data(self) -> Mapping[str, object]:
        return self._data

    @property
    def formats(self) -> Mapping[str, str]:
        """JSON keyword to string format annotation.

        .. warning::

            The is not completely reliable.
        """

        return self._formats

    @property
    def notes(self) -> Mapping[str, Note]:
        """The notes for each test case flag."""

        return self._notes

    @property
    def test_count(self) -> int | None:
        """The test count from the JSON "numberOfTests" value."""

        return self._test_count

    @property
    def schema_file(self) -> Path:
        """The path where the schema file was expected.

        The existence of this path does not mean that
        the file exists at that location.
        """

        return self._schema_file

    def schema_is_valid(self) -> bool:
        """True iff the JSON data properly validated against a valid schema.

        Note that this can be False if the schema failed to load.
        """

        return self._schema_status == "valid"

    def schema_is_loaded(self) -> bool:
        """True iff the schema file was found and read.

        That will be true even if the schema file is itself
        invalid.
        """

        return self._schema_status != "not-loaded"


class Loader:
    """Tools for loading Wycheproof test vectors."""

    def __init__(self, path: Path) -> None:
        """Establishes wycheproof data directory and pre-registers schemata.

        :param path:
            Path of wycheproof root directory

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
            retrieve=self._retrieve_from_dir,  # type: ignore[call-arg]
        )

    @property
    def root_dir(self) -> Path:
        """The absolute path of the wycheproof root directory."""
        return self._root_dir

    @classmethod
    def collect_formats(
        cls, schema: Mapping[str, object]
    ) -> Mapping[str, str]:
        """Collects format annotation for all string types in schema.

        :param schema:
            The schema from which to collect string format annotations.

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
    def _retrieve_from_dir(self, filename: str = "") -> Resource:
        """Retrieves schema from file system directory.
        Retrieval function to be passed to Registry.

        :param directory:
            A string representing the file system directory
            from which schemata are retrieved.
        """

        path = self._schemata_dir / filename
        contents = json.loads(path.read_text())
        return Resource.from_contents(contents, DRAFT202012)

    def load(
        self,
        path: Path | str,
        *,
        subdir: str = "testvectors_v1",
        strict_validation: bool = False,
    ) -> TestData:
        """Returns the file data

        :param path: relative path to json file with test vectors.
        :param subdir:
            The the subdirectory of wycheproof with the test vector to load.
        :param strict_validation: If true, fail if schema validation fails.

        :raises Exceptions:
            if the expected data file can't be found or read.

        :raises Exception:
            if strict_validation is True and schema validation fails.
        """

        path = self._root_dir / subdir / path

        try:
            with open(path, "r") as f:
                wycheproof_json = json.loads(f.read())
        except Exception as e:
            raise Exception(f"failed to load JSON: {e}")

        scheme_file = wycheproof_json["schema"]
        scheme_path = Path(self._schemata_dir / scheme_file)

        scheme: Mapping[str, object] = dict()
        schema_status: str = "not-loaded"
        formats: Mapping[str, str] = dict()
        try:
            with open(scheme_path, "r") as s:
                scheme = json.load(s)
                schema_status = "loaded"
        except Exception as e:
            msg = f"Schema loading failed: {e}"
            if strict_validation:
                raise Exception(msg)
            logging.warning(msg)

        if schema_status == "loaded":
            validator = validators.Draft202012Validator(
                schema=scheme,
                registry=self.registry,
            )  # type: ignore[misc]
            try:
                validator.validate(wycheproof_json)
                schema_status = "valid"
            except Exception as e:
                msg = f"JSON validation failed: {e}"
                if strict_validation:
                    raise Exception(msg)
                logging.warning(f"JSON validation failed: {e}")

            if schema_status == "valid":
                schemata_uri = (self._schemata_dir / "ALL_YOUR_BASE").as_uri()
                full_schema = jsonref.replace_refs(
                    scheme,
                    base_uri=schemata_uri,
                )
                assert isinstance(full_schema, dict)
                formats = self.collect_formats(full_schema)

        return TestData(
            wycheproof_json,
            formats,
            schema_path=scheme_path,
            schema_status=schema_status,
        )
