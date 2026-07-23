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
    parser.add_argument(
        "--source",
        required=True,
        action="append",
        type=pathlib.Path,
        help="CodeLinaro manifest; repeat for referenced techpack manifests",
    )
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--include", required=True)
    parser.add_argument(
        "--source-tag",
        required=True,
        action="append",
        help="Source tag recorded in the generated manifest comment",
    )
    parser.add_argument(
        "--path-prefix",
        action="append",
        default=[],
        help="Additional project path prefix to import",
    )
    parser.add_argument(
        "--project-path",
        action="append",
        default=[],
        help="Additional exact project path to import",
    )
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
    if len(args.source) != len(args.source_tag):
        raise ValueError("--source and --source-tag must have the same count")

    base = ET.parse(args.base).getroot()
    sources = [ET.parse(path).getroot() for path in args.source]
    base_by_path = {
        project.get("path"): project.get("name")
        for project in base.findall("project")
    }
    path_prefixes = (*QCOM_PATH_PREFIXES, *args.path_prefix)
    project_paths = set(args.project_path)

    output = ET.Element("manifest")
    output.append(
        ET.Comment(
            " Generated from CodeLinaro tags "
            + ", ".join(args.source_tag)
            + ". "
        )
    )
    ET.SubElement(output, "include", {"name": args.include})

    if args.add_remote:
        remote = next(
            (
                source.find("remote[@name='clo-la']")
                for source in sources
                if source.find("remote[@name='clo-la']") is not None
            ),
            None,
        )
        if remote is None:
            raise RuntimeError("source manifests have no clo-la remote")
        output.append(copy.deepcopy(remote))

    projects_by_path = {}
    for source in sources:
        for project in source.findall("project"):
            path = project.get("path", "")
            if path.startswith(path_prefixes) or path in project_paths:
                projects_by_path[path] = project
    projects = list(projects_by_path.values())

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
