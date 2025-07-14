#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
import os
import glob
import fnmatch


def find_files_in_dir(base_path: Path, max_level: int) -> list[Path]:
    files = []

    def _walk(current_path: Path, current_level: int):
        if current_level > max_level:
            return
        for entry in current_path.iterdir():
            if entry.name.startswith("."):
                continue  # skip hidden files like .DS_Store
            if entry.is_file():
                files.append(entry)
            elif entry.is_dir():
                _walk(entry, current_level + 1)

    _walk(base_path, 0)
    return files


def is_text_file(filepath: Path) -> bool:
    try:
        with filepath.open("rb") as f:
            chunk = f.read(8000)
        chunk.decode("utf-8")
        return True
    except Exception:
        return False


def print_file(filepath: Path, base_dir: Path = None):
    if not is_text_file(filepath):
        print(f"# Skipping non-text file: {filepath}", file=sys.stderr)
        return

    rel_path = filepath.relative_to(base_dir) if base_dir else filepath.name
    print("###")
    print(f"# {rel_path}")
    print("###")
    try:
        print(filepath.read_text())
    except Exception as e:
        print(f"# Error reading {filepath}: {e}", file=sys.stderr)


def should_exclude(filepath: Path, exclude_patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(filepath.name, pat) for pat in exclude_patterns)


def main():
    parser = argparse.ArgumentParser(
        description="Flatten and print files with header formatting."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to clip (default: current directory)",
    )
    parser.add_argument(
        "-L",
        "--level",
        type=int,
        default=0,
        help="Recursion level for directories (0 = current dir only)",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Glob patterns to exclude (e.g. --exclude '*.json' '*.png')",
    )
    args = parser.parse_args()

    all_files = []

    for path_str in args.paths:
        for resolved_str in glob.glob(path_str):
            path = Path(resolved_str)
            if path.is_file():
                all_files.append(path)
            elif path.is_dir():
                found = find_files_in_dir(path, args.level)
                all_files.extend(found)

    for f in sorted(all_files):
        if should_exclude(f, args.exclude):
            print(f"# Excluded by pattern: {f}", file=sys.stderr)
            continue
        base = (
            f.parents[args.level]
            if args.level > 0 and len(f.parents) > args.level
            else f.parent
        )
        print_file(f, base_dir=base)


if __name__ == "__main__":
    main()
