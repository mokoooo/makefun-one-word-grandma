#!/usr/bin/env python3
"""Write the one word for the make.fun bounty
"One Word From Grandma" (u-0xkianno-one-word-from-grandma-f04bed16).

The program has exactly one job: put a single fixed word of text into
``<output dir>/entry.txt``. The output directory comes from the
``MAKEFUN_OUTPUT_DIR`` environment variable and defaults to ``/output``,
the sandbox convention. The word is a constant, so repeated runs
produce byte-identical files.

The bounty gate accepts UTF-8 text of 1 to 30 characters, not only
white space. The word is checked against that rule before any file is
touched, so a bad word fails loudly instead of leaving a bad
output behind.

The file holds the word plus one trailing newline (11 bytes total).
The kit gate does not state whether a trailing newline is expected;
the single trailing newline is the builder's recorded assumption
(see BUILD.md). The word itself is 10 characters, so the file is
within the 30-character gate with or without the newline.

Standard library only. No network, no randomness, no arguments.
"""

import os
import sys
from pathlib import Path

WORD = "witchcraft"

# The file content: the word plus one trailing newline.
CONTENT = WORD + "\n"

MAX_CHARS = 30
OUTPUT_NAME = "entry.txt"
DEFAULT_OUTPUT_DIR = "/output"
FILE_MODE = 0o644


def validation_error(content: str) -> str | None:
    """Return why ``content`` fails the bounty gate, or None when it passes.

    Reasons are checked in a fixed order: embedded newline other than
    the single trailing one first, then blank, then too long.
    """
    body = content[:-1] if content.endswith("\n") else content
    if "\n" in body or "\r" in body:
        return f"embedded newline ({len(content)} chars)"
    if not body.strip():
        return f"blank or whitespace-only ({len(content)} chars)"
    if len(content) > MAX_CHARS:
        return f"too long: {len(content)} chars (max {MAX_CHARS})"
    if " " in body or "\t" in body:
        return "more than one word"
    return None


def is_valid_entry(content: str) -> bool:
    """True when the content fits the bounty gate: 1-30 chars, one
    word, not blank, and no embedded newline besides the trailing one."""
    return validation_error(content) is None


def write_entry(content: str, out_dir: Path) -> None:
    """Atomically write ``content`` to ``out_dir/entry.txt`` as mode 0644.

    The text goes to a temporary sibling file first and is renamed
    into place, so the grader can never read a half-written entry.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        # Best effort only: the directory may already exist under
        # another owner (e.g. a sandbox-prepared /output), and its
        # mode is irrelevant to the grader. Only the file's 0644
        # matters, because the grader reads it as a different user.
        os.chmod(out_dir, 0o755)
    except OSError:
        pass
    target = out_dir / OUTPUT_NAME
    tmp = out_dir / ("." + OUTPUT_NAME + f".{os.getpid()}.tmp")
    tmp.write_text(content, encoding="utf-8")
    os.chmod(tmp, FILE_MODE)
    # rename keeps the temp file's mode, so no second chmod is needed
    tmp.replace(target)


def main() -> int:
    if not is_valid_entry(CONTENT):
        error = validation_error(CONTENT)
        print(f"entry invalid: {error}", file=sys.stderr)
        return 1
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))
    write_entry(CONTENT, out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
