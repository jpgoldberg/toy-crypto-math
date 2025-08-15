"""Loading and parsing Wycheproof test data.

Assumes you have a local copy, clone (submodule) of
https://github.com/C2SP/wycheproof

Adapted from https://appsec.guide/docs/crypto/wycheproof/wycheproo_example/
"""

from collections.abc import Mapping
from pathlib import Path
import json
import typing

from jsonschema.protocols import Validator
from referencing import Resource, Registry


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
            retrieve=self.retrieve_from_fs,  # type: ignore[call-arg]
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

    @classmethod
    def collect_bigint_attrs(
        cls,
        node: object,
        attr: str = "",
    ) -> set[str]:
        """Collects properties that are hex strings".

        :param node:
            object returned by something like ``json.load()``,
            or a node within such an object in the recursive calls.
        :param attr: is the name of the current object

        Wycheproof schemata use ``{"type": "string", "format": "BigInt"}``
        or ``{"type": "string", "format": "HexBytes"}``
        for attributes that are hexadecimal strings to be converted to int.
        We need to collect the names of such attributes.

        .. note::

            There must be a more natural way use scheme annotations
            to help us process objects imported from JSON.
            But if there is, I have not yet found it.
        """

        acc: set[str] = set()

        if isinstance(node, dict):
            format = node.get("format")
            if (
                format in ("BigInt", "HexBytes")
                and node.get("type") == "string"
            ):
                acc.add(attr)
                return acc
            for key, value in node.items():
                acc |= cls.collect_bigint_attrs(value, key)

        elif isinstance(node, list):
            for n in node:
                acc |= cls.collect_bigint_attrs(n, "")
        return acc

    def retrieve_from_fs(self, directory: str = "") -> Resource:
        """Argument must be a str for reasons."""

        contents = json.loads(self._schemata_dir.read_text())
        return Resource.from_contents(contents)

    def load_json(
        self,
        path: Path | str,
        *,
        subdir: str = "testvectors",
    ) -> tuple[dict[str, object], Mapping[str, str]]:
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
        return wycheproof_json, formats

    @staticmethod
    def deserialize_top_level(
        properties: dict[str, object], formats: Mapping[str, str]
    ) -> None:
        """Mutates properties. Deserializes top level members according for format"""

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
                case "Asn":
                    # Leave as string, as it might be invalid
                    pass
                case "Der":
                    # TODO: either convert or issue warning
                    pass
                case "Pem":
                    # TODO: either convert or issue warning
                    pass
                case _:
                    pass

    def tests(
        self,
        path: str | Path,
        *,
        subdir: str = "testvectors",
    ) -> typing.Generator[Test, None, None]:
        data, formats = self.load_json(path, subdir=subdir)

        for group in data.pop("testGroups"):  # type: ignore
            self.deserialize_top_level(group, formats)

            cases: dict[str, object] = group.pop("tests")
            for c in cases:
                assert isinstance(c, dict)
                self.deserialize_top_level(c, formats)
                yield Test(data, group, c)
