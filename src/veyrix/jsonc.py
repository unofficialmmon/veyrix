"""Strict JSONC span parsing; update only requested values, retain other bytes."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from .common import Error, require

TOKEN = re.compile(r'\s+|//[^\r\n]*|/\*[\s\S]*?\*/|"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*"|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?|true|false|null|[{}\[\],:]')


@dataclass
class Node:
    value: Any
    start: int
    end: int
    children: dict[str, "Node"] = field(default_factory=dict)
    trailing_comma: bool = False


class Parser:
    def __init__(self, text: str):
        self.text = text
        self.tokens: list[tuple[str, int, int]] = []
        pos = 0
        while pos < len(text):
            match = TOKEN.match(text, pos)
            require(match is not None, "INVALID_JSONC", f"Invalid token at offset {pos}")
            assert match is not None
            token = match.group()
            if not token.isspace() and not token.startswith(("//", "/*")):
                self.tokens.append((token, pos, match.end()))
            pos = match.end()
        self.i = 0

    def pop(self, expected: str | None = None) -> tuple[str, int, int]:
        require(self.i < len(self.tokens), "INVALID_JSONC", "Unexpected end of JSONC")
        token = self.tokens[self.i]
        require(expected is None or token[0] == expected,
                "INVALID_JSONC", f"Expected {expected}, got {token[0]}")
        self.i += 1
        return token

    def peek(self) -> str:
        return self.tokens[self.i][0] if self.i < len(self.tokens) else ""

    def node(self, depth: int = 0) -> Node:
        require(depth < 60, "INVALID_JSONC", "JSONC nesting too deep")
        token, start, end = self.pop()
        if token in ("{", "["):
            is_object = token == "{"
            value: Any = {} if is_object else []
            children = {}
            close = "}" if is_object else "]"
            trailing = False
            while self.peek() != close:
                if is_object:
                    name, _, _ = self.pop()
                    require(name.startswith('"'), "INVALID_JSONC", "Object key must be a string")
                    key = json.loads(name)
                    require(key not in value, "DUPLICATE_KEY", f"Duplicate JSONC key: {key}")
                    self.pop(":")
                    child = self.node(depth + 1)
                    value[key] = child.value
                    children[key] = child
                else:
                    value.append(self.node(depth + 1).value)
                if self.peek() != ",":
                    break
                self.pop(",")
                trailing = self.peek() == close
                if trailing:
                    break
            _, _, end = self.pop(close)
            return Node(value, start, end, children, trailing)
        try:
            return Node(json.loads(token), start, end)
        except ValueError as exc:
            raise Error("INVALID_JSONC", f"Invalid value: {token}") from exc

    def parse(self) -> Node:
        root = self.node()
        require(self.i == len(self.tokens), "INVALID_JSONC", "Unexpected trailing JSONC")
        require(isinstance(root.value, dict), "SCHEMA", "OMO config must be an object")
        return root


def parse(text: str) -> Node:
    return Parser(text).parse()


def set_value(text: str, path: tuple[str, ...], value: Any) -> str:
    root = parse(text)
    node = root
    for index, key in enumerate(path):
        require(isinstance(node.value, dict), "SCHEMA", f"Not an object at {path[:index]}")
        child = node.children.get(key)
        if child is not None:
            if index == len(path) - 1:
                if child.value == value:
                    return text
                return text[:child.start] + json.dumps(value, ensure_ascii=False) + text[child.end:]
            node = child
            continue
        nested = value
        for remaining in reversed(path[index + 1:]):
            nested = {remaining: nested}
        # Inserting before a closing brace is safe even after an EOF line comment:
        # the newline terminates the comment and keeps all existing tokens intact.
        prefix = "," if node.value and not node.trailing_comma else ""
        addition = "\n" + prefix + json.dumps(key) + ": " + json.dumps(nested, ensure_ascii=False) + "\n"
        result = text[:node.end - 1] + addition + text[node.end - 1:]
        parse(result)
        return result
    raise Error("SCHEMA", "Empty JSON path")


def reconcile(text: str, desired: dict[str, list[str]], owned: dict[str, list[str]]) -> tuple[str, dict]:
    """Track only added IDs; preserve manual additions and every unrelated field."""
    parsed = parse(text).value
    agents = parsed.get("agents", {})
    require(isinstance(agents, dict), "SCHEMA", "agents must be an object")
    new_owned = {}
    for agent in sorted(set(desired) | set(owned)):
        conf = agents.get(agent, {})
        require(isinstance(conf, dict), "SCHEMA", f"Invalid agent: {agent}")
        current = conf.get("skills_add", [])
        require(isinstance(current, list) and all(isinstance(x, str) for x in current)
                and len(current) == len(set(current)), "SCHEMA", f"Invalid skills_add: {agent}")
        previous = owned.get(agent, [])
        require(set(previous) <= set(current), "MANAGED_MODIFIED", f"Owned OMO grant removed: {agent}")
        wanted = desired.get(agent, [])
        base_grants = conf.get("skills", [])
        require(isinstance(base_grants, list) and all(isinstance(x, str) for x in base_grants),
                "SCHEMA", f"Invalid skills: {agent}")
        require(not any(x == "!*" or x.startswith("!") and x[1:] in wanted for x in base_grants),
                "ROUTING_DENIED", f"Project skills exclusions conflict: {agent}")
        removed = conf.get("skills_remove", [])
        require(isinstance(removed, list) and all(isinstance(x, str) for x in removed),
                "SCHEMA", f"Invalid skills_remove: {agent}")
        require(not any(x == "*" or x in wanted for x in removed),
                "ROUTING_DENIED", f"Project skills_remove conflicts: {agent}")
        manual = [x for x in current if x not in previous]
        additions = [x for x in wanted if x not in manual]
        result = manual + additions
        if result != current or agent in desired and "skills_add" not in conf:
            text = set_value(text, ("agents", agent, "skills_add"), result)
        if additions:
            new_owned[agent] = additions
    return text, new_owned
