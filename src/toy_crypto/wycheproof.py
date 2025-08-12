"""Loading and parsing Wycheproof test data.

Assumes you have a local copy, clone (submodule) of
https://github.com/C2SP/wycheproof

Adapted from https://appsec.guide/docs/crypto/wycheproof/wycheproo_example/
"""

import os
from pathlib import Path
from importlib.resources import files, as_file
from importlib.resources.abc import Traversable
import json
from jsonschema.protocols import Validator
from referencing import Resource, Registry

type WyVector = dict[str, object]


class WycheproofLoad:
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
            raise NotADirectoryError("Couldn't find 'schamas' directory")

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
