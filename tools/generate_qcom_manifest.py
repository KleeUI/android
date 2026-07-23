#!/usr/bin/env python3
#
# Copyright (C) 2026 The KleeUI Project
#
# SPDX-License-Identifier: Apache-2.0

"""Generate a pinned optional Qualcomm manifest from a CodeLinaro release."""

import argparse
import copy
import pathlib
import xml.etree.ElementTree as ET


QCOM_PATH_PREFIXES = (
    "device/qcom/",
    "hardware/qcom/",
    "vendor/qcom/opensource/",
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, type=pathlib.Path)
    parser.add_argument("--source", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--include", required=True)
    parser.add_argument("--source-tag", required=True)
    parser.add_argument("--add-remote", action="store_true")
    return parser.parse_args()


def indent(element, level=0):
    prefix = "\n" + "  " * level
    child_prefix = "\n" + "  " * (level + 1)
    if len(element):
        if not element.text or not element.text.strip():
            element.text = child_prefix
        for child in element:
            indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = child_prefix
        element[-1].tail = prefix
    elif level and (not element.tail or not element.tail.strip()):
        element.tail = prefix


def main():
    args = parse_args()
    base = ET.parse(args.base).getroot()
    source = ET.parse(args.source).getroot()
    base_by_path = {
        project.get("path"): project.get("name")
        for project in base.findall("project")
    }

    output = ET.Element("manifest")
    output.append(ET.Comment(f" Generated from CodeLinaro tag {args.source_tag}. "))
    ET.SubElement(output, "include", {"name": args.include})

    if args.add_remote:
        remote = source.find("remote[@name='clo-la']")
        if remote is None:
            raise RuntimeError("source manifest has no clo-la remote")
        output.append(copy.deepcopy(remote))

    projects = [
        project
        for project in source.findall("project")
        if project.get("path", "").startswith(QCOM_PATH_PREFIXES)
    ]

    removed = set()
    for project in projects:
        path = project.get("path")
        existing_name = base_by_path.get(path)
        if existing_name and existing_name not in removed:
            ET.SubElement(
                output,
                "remove-project",
                {"name": existing_name, "optional": "true"},
            )
            removed.add(existing_name)

    for project in projects:
        pinned = copy.deepcopy(project)
        pinned.set("clone-depth", "1")
        output.append(pinned)

    indent(output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(output).write(
        args.output,
        encoding="UTF-8",
        xml_declaration=True,
        short_empty_elements=True,
    )
    with args.output.open("ab") as stream:
        stream.write(b"\n")


if __name__ == "__main__":
    main()
