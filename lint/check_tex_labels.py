#!/usr/bin/env python3

"""Verify all labels defined by \label commands are referenced at least once,
and verify that all ref commands refer to a defined label."""

import os
import re
import sys


class Label:
    def __init__(self, filename, line_number, name):
        self.filename = filename
        self.line_number = line_number
        self.name = name

    def __lt__(self, other):
        return self.filename < other.filename or (
            self.filename == other.filename and self.line_number < other.line_number
        )


rgx = re.compile(r"\\(?P<command>(footref|eqref|ref|label)){(?P<arg>[^}]+)}")

files = [
    os.path.join(dp, f)[2:]
    for dp, dn, fn in os.walk(".")
    for f in fn
    if f.endswith(".tex") and "build/venv/" not in dp
]

labels = set()
refs = set()

# Maps from label name to tuple of filename and line number. This is used to
# print error diagnostics.
label_locations = {}
ref_locations = {}

for filename in files:
    # Get file contents
    with open(filename, "r") as f:
        contents = f.read()

    for match in rgx.finditer(contents):
        # Get line regex match was on
        linecount = 1
        for i in range(match.start()):
            if contents[i] == os.linesep:
                linecount += 1

        if match.group("command") == "label":
            label = match.group("arg")
            labels.add(label)
            label_locations[label] = Label(filename, linecount, label)
        elif "ref" in match.group("command"):
            ref = match.group("arg")
            refs.add(ref)
            ref_locations[ref] = Label(filename, linecount, ref)

undefined_refs = refs - labels
unrefed_labels = labels - refs

if labels == refs:
    # If labels and refs are equivalent sets, there are no undefined references
    # or unreferenced labels, so return success
    sys.exit(0)

if undefined_refs:
    print(f"error: {len(undefined_refs)} undefined reference", end="")
    if len(undefined_refs) > 1:
        print("s", end="")
    print(":")

    # Print refs sorted by filename and line number
    for ref in sorted(ref_locations[l] for l in undefined_refs):
        print(f"[{ref.filename}:{ref.line_number}]\n    {ref.name}")

if unrefed_labels:
    print(f"error: {len(unrefed_labels)} unreferenced label", end="")
    if len(unrefed_labels) > 1:
        print("s", end="")
    print(":")

    # Print labels sorted by filename and line number
    for label in sorted(label_locations[l] for l in unrefed_labels):
        print(f"[{label.filename}:{label.line_number}]\n    {label.name}")

sys.exit(1)
