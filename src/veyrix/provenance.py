"""Installed-source provenance. Never falls back to a moving ref."""
from __future__ import annotations
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
from . import __version__
from .common import Error, SHA, load_json, require
from .source import repository

DISTRIBUTION = "veyrix-cli"

def installed_source(allow_local: bool = False) -> dict[str, str]:
    try:
        dist = distribution(DISTRIBUTION)
        raw = dist.read_text("direct_url.json")
        require(isinstance(raw, str) and 0 < len(raw) <= 65536, "PIN_REQUIRED",
                "Installed VCS metadata is missing or too large")
        obj = load_json(raw)
        require(isinstance(obj, dict) and not {"dir_info", "archive_info"} & set(obj)
                and obj.get("subdirectory", "") == "", "PIN_REQUIRED",
                "Install provenance is not a root non-editable Git source")
        vcs = obj.get("vcs_info")
        require(isinstance(vcs, dict) and vcs.get("vcs") == "git"
                and isinstance(vcs.get("commit_id"), str)
                and SHA.fullmatch(vcs["commit_id"]) is not None, "PIN_REQUIRED",
                "Installed source has no immutable Git commit_id")
        url = repository(obj.get("url", ""), allow_local)
        running = Path(__file__).with_name("__init__.py").resolve(strict=True)
        owner = Path(dist.locate_file("veyrix/__init__.py")).resolve(strict=True)
        require(owner == running and dist.version == __version__, "PIN_REQUIRED",
                "Installed metadata does not identify the running Veyrix package")
        return {"repository": url, "commit": vcs["commit_id"], "evidence": "INSTALLED_VCS_METADATA"}
    except (PackageNotFoundError, OSError, UnicodeError, ValueError, TypeError,
            KeyError, RecursionError, Error) as exc:
        raise Error("PIN_REQUIRED",
                    "The running CLI has no usable installed-source provenance; provide an explicit full --ref") from exc

def installed_pin(expected_repository: str, allow_local: bool = False) -> str:
    source = installed_source(allow_local)
    expected = repository(expected_repository, allow_local)
    def identity(url: str) -> str:
        return url.rstrip("/").removesuffix(".git")
    require(identity(source["repository"]) == identity(expected), "PIN_REQUIRED",
            "Installed source differs from the selected repository; provide its full --ref")
    return source["commit"]
