from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .core import LEVELS, filter_entries, parse_line, read_entries, summarize

VERSION = "1.0.0"

def _filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("files", nargs="+", help="UTF-8 text or JSONL log files")
    parser.add_argument("--level", default="TRACE", choices=LEVELS, help="Minimum severity")
    parser.add_argument("--query", help="Case-insensitive text search")
    parser.add_argument("--regex", action="store_true", help="Treat --query as a regular expression")
    parser.add_argument("--agent", help="Exact agent/agent_id filter")
    parser.add_argument("--event", help="Exact event/type filter")
    parser.add_argument("--since", help="ISO-8601 lower timestamp bound")
    parser.add_argument("--until", help="ISO-8601 upper timestamp bound")

def _selected(args):
    return filter_entries(read_entries(args.files), min_level=args.level, query=args.query, agent=args.agent,
                          event=args.event, since=args.since, until=args.until, regex=args.regex)

def _render(entry, json_output: bool) -> str:
    if json_output:
        return json.dumps(entry.to_dict(), ensure_ascii=False)
    ts = entry.timestamp or "-"
    context = " ".join(x for x in [f"agent={entry.agent}" if entry.agent else "", f"event={entry.event}" if entry.event else ""] if x)
    return f"{ts} {entry.level:<8} {context + ' ' if context else ''}{entry.message}"

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-log-viewer", description="Inspect AI-agent logs locally.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION} — Radwan Abdulhadi Ahmed / @rad03i2")
    sub = parser.add_subparsers(dest="command", required=True)
    view = sub.add_parser("view", help="Filter and print entries")
    _filters(view); view.add_argument("--json", action="store_true"); view.add_argument("--limit", type=int, default=0)
    stats = sub.add_parser("stats", help="Summarize matching entries")
    _filters(stats); stats.add_argument("--json", action="store_true")
    follow = sub.add_parser("follow", help="Follow one file like tail -f")
    follow.add_argument("file"); follow.add_argument("--from-start", action="store_true"); follow.add_argument("--interval", type=float, default=.5)
    follow.add_argument("--level", default="TRACE", choices=LEVELS); follow.add_argument("--query"); follow.add_argument("--json", action="store_true")
    return parser

def main(argv=None) -> int:
    parser = build_parser(); args = parser.parse_args(argv)
    try:
        if args.command == "view":
            if args.limit < 0: raise ValueError("--limit cannot be negative")
            count = 0
            for entry in _selected(args):
                print(_render(entry, args.json)); count += 1
                if args.limit and count >= args.limit: break
            return 0
        if args.command == "stats":
            data = summarize(_selected(args))
            if args.json: print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                print(f"Entries: {data['total']}")
                print("Levels: " + (", ".join(f"{k}={v}" for k,v in sorted(data['levels'].items())) or "none"))
                print("Agents: " + (", ".join(f"{k}={v}" for k,v in sorted(data['agents'].items())) or "none"))
                print("Events: " + (", ".join(f"{k}={v}" for k,v in sorted(data['events'].items())) or "none"))
                print(f"Range: {data['first_timestamp'] or '-'} → {data['last_timestamp'] or '-'}")
            return 0
        path = Path(args.file)
        if not path.is_file(): raise FileNotFoundError(f"Log file not found: {path}")
        if args.interval <= 0: raise ValueError("--interval must be greater than zero")
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            if not args.from_start: handle.seek(0, 2)
            line_no = 0
            while True:
                raw = handle.readline()
                if not raw: time.sleep(args.interval); continue
                line_no += 1; entry = parse_line(raw, source=str(path), line=line_no)
                if entry and next(filter_entries([entry], min_level=args.level, query=args.query), None): print(_render(entry, args.json), flush=True)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2
    except KeyboardInterrupt:
        return 130
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
