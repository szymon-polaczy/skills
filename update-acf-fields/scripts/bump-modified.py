#!/usr/bin/env python3
"""Set ACF JSON 'modified' to current Unix timestamp without reformatting the file."""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

MODIFIED_RE = re.compile(r'("modified"\s*:\s*)\d+')


def bump_modified(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    ts = int(time.time())
    new_text, count = MODIFIED_RE.subn(rf"\g<1>{ts}", text, count=1)
    if count == 0:
        raise SystemExit(f'No "modified" key found in {path}')
    if new_text == text:
        raise SystemExit(f'"modified" already {ts} in {path}')
    path.write_text(new_text, encoding="utf-8")
    return ts


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(f"Usage: {sys.argv[0]} <acf-json-file> [more-files...]")

    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.is_file():
            raise SystemExit(f"Not a file: {path}")
        ts = bump_modified(path)
        print(f"{path}: modified -> {ts}")


if __name__ == "__main__":
    main()
