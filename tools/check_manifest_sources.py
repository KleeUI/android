#!/usr/bin/env python3
#
# Copyright (C) 2026 The KleeUI Project
#
# SPDX-License-Identifier: Apache-2.0

"""Validate the source boundary declared by Klee manifests."""

import pathlib
import re
import sys
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFESTS = (ROOT / "default.xml", *sorted((ROOT / "qcom").glob("*.xml")))
ALLOWED_REMOTES = {
    "aosp": "https://android.googlesource.com",
    "clo-la": "https://git.codelinaro.org/clo/la",
    "klee": "https://github.com/KleeUI",
}
PINNED_REVISION = re.compile(r"[0-9a-f]{40}")


def fail(message):
    print(f"source-policy: {message}", file=sys.stderr)
    return 1


def main():
    failures = 0

    for manifest in MANIFESTS:
        root = ET.parse(manifest).getroot()
        label = manifest.relative_to(ROOT)

        for remote in root.findall("remote"):
            name = remote.get("name", "")
            fetch = remote.get("fetch", "").rstrip("/")
            if ALLOWED_REMOTES.get(name) != fetch:
                failures += fail(
                    f"{label}: remote {name!r} has unapproved fetch {fetch!r}"
                )

        for project in root.findall("project"):
            remote = project.get("remote")
            if remote and remote not in ALLOWED_REMOTES:
                failures += fail(
                    f"{label}: project {project.get('name')!r} uses "
                    f"unapproved remote {remote!r}"
                )

            if remote == "clo-la":
                revision = project.get("revision", "")
                if not PINNED_REVISION.fullmatch(revision):
                    failures += fail(
                        f"{label}: CodeLinaro project {project.get('name')!r} "
                        "is not pinned to a full commit"
                    )
                if project.get("clone-depth") != "1":
                    failures += fail(
                        f"{label}: CodeLinaro project {project.get('name')!r} "
                        "must use clone-depth=1"
                    )

    if failures:
        return 1

    print(
        f"source-policy: validated {len(MANIFESTS)} manifests "
        "against the AOSP, CodeLinaro, and KleeUI source boundary"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
