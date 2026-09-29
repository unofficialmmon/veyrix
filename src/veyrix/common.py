"""Small strict parsers and filesystem guards shared by the CLI."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")


class Error(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise Error(code, message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, "DUPLICATE_KEY", f"Duplicate key: {key}")
        result[key] = value
    return result


def load_json(data: bytes | str) -> Any:
    try:
        return json.loads(data, object_pairs_hook=unique_pairs,
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, UnicodeError) as exc:
        raise Error("INVALID_JSON", str(exc)) from exc


class StrictLoader(yaml.SafeLoader):
    pass


def _mapping(loader: StrictLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    return unique_pairs([(loader.construct_object(k, deep=deep),
                          loader.construct_object(v, deep=deep)) for k, v in node.value])


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def load_yaml(data: bytes | str) -> Any:
    try:
        return yaml.load(data, Loader=StrictLoader)
    except (yaml.YAMLError, TypeError, UnicodeError, RecursionError) as exc:
        raise Error("INVALID_YAML", str(exc)) from exc


def safe_rel(text: str) -> str:
    require(isinstance(text, str) and bool(text), "UNSAFE_PATH", "Empty/non-string path")
    p = PurePosixPath(text)
    require(not p.is_absolute() and str(p) == text and
            all(part not in (".", "..", ".git") for part in p.parts) and
            not any(c in text for c in ("\\", ":", "\0", "\n", "\r")),
            "UNSAFE_PATH", f"Unsafe relative path: {text!r}")
    return text


def guarded(root: Path, rel: str) -> Path:
    """Reject symlinks at every managed component, including dangling links."""
    target = root / safe_rel(rel)
    here = root
    require(not root.is_symlink(), "SYMLINK", f"Symlink project root: {root}")
    for part in PurePosixPath(rel).parts:
        here = here / part
        require(not here.is_symlink(), "SYMLINK", f"Refusing symlink: {here}")
        if here != target and here.exists():
            require(here.is_dir(), "PATH_TYPE", f"Not a directory: {here}")
    return target


def read_regular(path: Path) -> bytes | None:
    require(not path.is_symlink(), "SYMLINK", f"Refusing symlink: {path}")
    if not path.exists():
        return None
    s = path.stat()
    require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1,
            "PATH_TYPE", f"Not an independent regular file: {path}")
    require(s.st_size <= 4 * 1024 * 1024, "SIZE_LIMIT", f"File too large: {path}")
    return path.read_bytes()


def ids(value: Any, label: str) -> list[str]:
    require(isinstance(value, list) and all(isinstance(x, str) and ID.fullmatch(x)
                                         for x in value), "SCHEMA", f"Invalid IDs: {label}")
    require(len(value) == len(set(value)), "SCHEMA", f"Duplicate IDs: {label}")
    return value


def config_home() -> Path:
    if os.environ.get("OPENCODE_CONFIG_DIR"):
        return Path(os.environ["OPENCODE_CONFIG_DIR"]).expanduser()
    return Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "opencode"
