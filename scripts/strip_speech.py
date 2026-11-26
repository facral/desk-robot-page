#!/usr/bin/env python3
"""Copy an events file without the participant's words, so it can be shared or analysed safely.

Rows of type `heard` keep who the speech was for (robot, answer, listen, none); the text after `|` is removed.
Usage: python scripts/strip_speech.py CODE_laptop_events.csv   -> writes CODE_laptop_events_nospeech.csv
"""
import csv
import sys

src = sys.argv[1]
dst = src[:-4] + "_nospeech.csv"
with open(src, encoding="utf-8-sig", newline="") as f:
    lines = f.read().splitlines()
head = [l for l in lines if l.startswith("#")]
rows = list(csv.reader(l for l in lines if not l.startswith("#")))
for r in rows[1:]:
    if len(r) == 3 and r[1] == "heard":
        r[2] = r[2].split("|", 1)[0] + "|"
with open(dst, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(head) + "\n")
    csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator="\n").writerows(rows)
assert not any(r[1] == "heard" and not r[2].endswith("|") for r in rows[1:] if len(r) == 3)
print("wrote", dst)
