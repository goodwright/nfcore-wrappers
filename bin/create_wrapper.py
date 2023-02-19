#!/usr/bin/env python3

"""TODO"""

import argparse
import logging
import os
from os import path
from sys import exit
from pathlib import Path

import rich
import rich.console
import rich.logging
import rich.traceback

log = logging.getLogger()
stderr = rich.console.Console(stderr=True)
stdout = rich.console.Console()
rich.traceback.install(console=stderr, width=200, word_wrap=True, extra_lines=1)

def resolve_input(input):
    resolved = False
    start_index = 0
    output = {"text": input, "vars": []}
    input_split = input.split(',')

    if "tuple" in input_split[0]:
        # Will be in format tuple val(meta), arg1, arg2, arg3
        # Need to parse the last n args
        start_index = 1
    
    input_split = input_split[start_index:]
    
    for arg in input_split:
        arg_st = arg.strip()
        arg_info = {"type": "UNKNOWN"}

        if "val" in arg_st:
            arg_info["type"] = "val"
            arg_info["name"] = arg_st.replace("val", "").replace("(","").replace(")","").strip()
            output["vars"].append(arg_info)
        if "path" in arg_st:
            arg_info["type"] = "path"
            arg_info["name"] = arg_st.replace("path", "").replace("(","").replace(")","").strip()
            output["vars"].append(arg_info)

    return output


def main(target):
    log.info("Create Wrapper")
    log.info(f"Target: {target}")

    # Build module paths and check the files exist
    main_path = path.join("./modules/nf-core", target, "main.nf")
    meta_path = path.join("./modules/nf-core", target, "meta.yml")

    if os.path.isfile(main_path) == False:
        log.error(f"Path does not exist {main_path}")
        exit(1)

    if os.path.isfile(meta_path) == False:
        log.error(f"Path does not exist {meta_path}")
        exit(1)

    # Calc module name
    module_name = '_'.join(target.split('/')).upper()

    # Scan module
    log.info(f"Scanning module {module_name}")

    # Parse the input lines
    inputs = []
    in_range = False
    with open(Path(main_path), "r") as fh:
        for line in fh:
            line_st = line.strip()
            if line_st == "input:":
                in_range = True
                continue
            if in_range and line_st == "output:":
                in_range = False
                continue

            if in_range and line_st != "":
                inputs.append(line_st)
    log.info(f"Found {len(inputs)} inputs")

    input_info = []
    for input in inputs:
        r_input = resolve_input(input)
        input_info.append(r_input)
        log.info(r_input)

    log.info(f"Creating wrapper for {module_name}")


if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    args = parser.parse_args()

    # Setup logging
    log.setLevel(logging.DEBUG)
    log.addHandler(
        rich.logging.RichHandler(
            level=logging.DEBUG,
            console=rich.console.Console(stderr=True),
            show_time=False,
            show_path=True,
            markup=True,
        )
    )

    # Run main
    main(args.target)
