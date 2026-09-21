from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

LEVELS = {"TRACE": 5, "DEBUG": 10, "INFO": 20, "WARN": 30, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
TEXT_RE = re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2}[T ][^ ]+)\s+(?:\[(?P<level1>[A-Za-z]+)\]|(?P<level2>[A-Za-z]+))\s+(?P<message>.*)$")

@dataclass(frozen=True)
class Entry:
    timestamp: str | None
    level: str
    message: str
    agent: str | None = None
    event: str | None = None
    source: str | None = None
    line: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_level(value: object) -> str:
    level = str(value or "INFO").upper()
    return "WARN" if level == "WARNING" else level if level in LEVELS else "INFO"


def parse_line(raw: str, *, source: str | None = None, line: int | None = None) -> Entry | None:
    text = raw.strip()
    if not text:
        return None
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        obj = None
    if isinstance(obj, dict):
        message = obj.get("message", obj.get("msg", obj.get("content", "")))
        if not isinstance(message, str):
            message = json.dumps(message, ensure_ascii=False, separators=(",", ":"))
        return Entry(
            timestamp=str(obj.get("timestamp") or obj.get("time") or obj.get("ts") or "") or None,
            level=normalize_level(obj.get("level") or obj.get("severity")),
            message=message,
            agent=str(obj.get("agent") or obj.get("agent_id") or "") or None,
            event=str(obj.get("event") or obj.get("type") or "") or None,
            source=source, line=line,
        )
    match = TEXT_RE.match(text)
    if match:
        return Entry(match.group("ts"), normalize_level(match.group("level1") or match.group("level2")), match.group("message"), source=source, line=line)
    return Entry(None, "INFO", text, source=source, line=line)


def read_entries(paths: Iterable[str | Path]) -> Iterator[Entry]:
    for item in paths:
        path = Path(item)
        if not path.is_file():
            raise FileNotFoundError(f"Log file not found: {path}")
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for number, raw in enumerate(handle, 1):
                entry = parse_line(raw, source=str(path), line=number)
                if entry:
                    yield entry


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    candidate = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(candidate)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def filter_entries(entries: Iterable[Entry], *, min_level: str = "TRACE", query: str | None = None,
                   agent: str | None = None, event: str | None = None, since: str | None = None,
                   until: str | None = None, regex: bool = False) -> Iterator[Entry]:
    threshold = LEVELS.get(normalize_level(min_level), 5)
    start, end = _parse_time(since), _parse_time(until)
    if since and not start:
        raise ValueError("--since must be an ISO-8601 timestamp")
    if until and not end:
        raise ValueError("--until must be an ISO-8601 timestamp")
    pattern = re.compile(query, re.IGNORECASE) if query and regex else None
    for entry in entries:
        if LEVELS.get(entry.level, 20) < threshold:
            continue
        if agent and (entry.agent or "").casefold() != agent.casefold():
            continue
        if event and (entry.event or "").casefold() != event.casefold():
            continue
        haystack = " ".join(filter(None, [entry.message, entry.agent, entry.event]))
        if query and not (pattern.search(haystack) if pattern else query.casefold() in haystack.casefold()):
            continue
        when = _parse_time(entry.timestamp)
        if start and (not when or when < start):
            continue
        if end and (not when or when > end):
            continue
        yield entry


def summarize(entries: Iterable[Entry]) -> dict:
    rows = list(entries)
    levels = Counter(row.level for row in rows)
    agents = Counter(row.agent for row in rows if row.agent)
    events = Counter(row.event for row in rows if row.event)
    times = [t for row in rows if (t := _parse_time(row.timestamp))]
    return {"total": len(rows), "levels": dict(levels), "agents": dict(agents), "events": dict(events),
            "first_timestamp": min(times).isoformat() if times else None,
            "last_timestamp": max(times).isoformat() if times else None}
