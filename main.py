"""Seventeen Syllables of Debugging — make.fun entry.

Writes one haiku about debugging (three lines, 5-7-5 syllables, at most
200 characters) as plain text to /output/entry.txt (or
$MAKEFUN_OUTPUT_DIR/entry.txt), then reads it back and verifies the gate:
exactly three non-empty lines, syllable shape 5-7-5, at most 200
characters. Standard library only.
"""

import os

HAIKU_LINES = [
    "One print left in prod",
    "it leaks my notes to the logs",
    "users read them too",
]

EXPECTED_SYLLABLES = [5, 7, 5]
MAX_CHARS = 200

VOWELS = "aeiou"


def count_syllables(word):
    """Heuristic syllable count: vowel groups, silent trailing 'e',
    and a trailing 'y' acting as a vowel."""
    w = "".join(ch for ch in word.lower() if ch.isalpha())
    if not w:
        return 0
    count = 0
    prev_vowel = False
    for i, ch in enumerate(w):
        is_vowel = ch in VOWELS or (ch == "y" and i > 0)
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Silent trailing 'e' (e.g. "One") or the 'e' in a trailing "es"
    # after a consonant (e.g. "notes") does not add a syllable.
    if w.endswith("e") and count > 1:
        count -= 1
    elif w.endswith("es") and len(w) > 2 and w[-3] not in VOWELS and count > 1:
        count -= 1
    return max(count, 1)


def check_haiku(text):
    """Return a list of gate failures (empty when the haiku passes)."""
    failures = []
    if not (1 <= len(text) <= MAX_CHARS):
        failures.append("length %d not in 1..%d" % (len(text), MAX_CHARS))
    if not text.strip():
        failures.append("entry is only whitespace")
    lines = text.split("\n")
    if len(lines) != 3:
        failures.append("expected 3 lines, got %d" % len(lines))
    for line, expected in zip(lines, EXPECTED_SYLLABLES):
        got = sum(count_syllables(w) for w in line.split())
        if got != expected:
            failures.append(
                "line %r has %d syllables, expected %d" % (line, got, expected)
            )
    return failures


def main():
    text = "\n".join(HAIKU_LINES)
    failures = check_haiku(text)
    if failures:
        raise SystemExit("haiku gate failed: " + "; ".join(failures))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    # Read it back and verify what actually landed on disk.
    with open(path, "r", encoding="utf-8") as f:
        written = f.read()
    failures = check_haiku(written)
    if failures or written != text:
        raise SystemExit("written entry failed gate: " + "; ".join(failures))
    print("wrote %s (%d characters, 3 lines, 5-7-5)" % (path, len(written)))


if __name__ == "__main__":
    main()
