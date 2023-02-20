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

test_data_paths = {
    "fasta" : "https://raw.githubusercontent.com/nf-core/test-datasets/modules/data/genomics/sarscov2/genome/genome.fasta"
}

file_type_info = {
    "fasta" : { "name": "FASTA", "type": "file", "pattern": "fa$|fasta$|fa\\\.gz$|fasta\\\.gz$", "desc": "A genome FASTA file"}
}

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

    # Write the wrapper
    log.info(f"Creating wrapper for {module_name}")

    file_list = []
    channel_list = []
    param_list = []

    for input in input_info:
        input_name = input['vars'][0]['name']
        file_str = f"ch_{input_name} = "

        if "meta" not in input['text']:
            if len(input['vars']) == 1:
                file_str = file_str + f"file(params.{input_name}, checkIfExists: true)"
                param_list.append(input_name)
            else:
                file_str = file_str + "["
                for var in input['vars']:
                    file_str = file_str + f"file(params.{var['name']}, checkIfExists: true), "
                file_str = file_str[:-2]
                file_str = file_str + "]"
        else:
            file_str = file_str + f"[ id:params.{input_name}.baseName, "

            if len(input['vars']) == 1:
                file_str = file_str + f"file(params.{input_name}, checkIfExists: true) "
                param_list.append(input_name)
            else:
                for var in input['vars']:
                    file_str = file_str + f"file(params.{var['name']}, checkIfExists: true), "
                    param_list.append(var['name'])
                file_str = file_str[:-2]
            
            file_str = file_str + "]"

        file_list.append(file_str)
        channel_list.append(f"ch_{input_name}")

    wrapper_path = path.join("./wrappers", module_name.lower() + ".nf")
    with open(Path(wrapper_path), "w") as fh:
        fh.write("nextflow.enable.dsl=2\n\n")
        fh.write(f"include {{ {module_name} }} from \"../modules/nf-core/{target}/main\" \n\n")
        fh.write("workflow {\n\n")

        for file_str in file_list:
            fh.write(f"    {file_str}\n")

        fh.write(f"\n    {module_name} (\n")

        for idx, param in enumerate(channel_list):
            if idx == 0:
                fh.write(f"        {param}")
            else:
                fh.write(f",\n        {param}")

        fh.write(f"\n    )\n\n")
        fh.write("}\n")

    # Write the test
    log.info(f"Creating test for {module_name}")
    test_path = path.join("./tests/wrappers/", "test_" + module_name.lower() + ".yml")

    command_str = f"command: nextflow run ./wrappers/{module_name.lower()}.nf -c ./tests/config/nextflow.config "
    for param in param_list:
        command_str = command_str + f"--{param} "
        if param in test_data_paths:
            command_str = command_str + f"{test_data_paths[param]} "
        else:
            command_str = command_str + "{PARAM-TODO}"

    with open(Path(test_path), "w") as fh:
        fh.write(f"- name: \"test_wrappers_{module_name.lower()}\"\n")
        fh.write(f"  {command_str}\n")
        fh.write("  tags:\n")
        fh.write("    - \"wrappers/\"\n")
        fh.write("    - \"wrappers/modules\"\n")
        fh.write(f"    - \"wrappers/modules/{module_name.lower()}\"\n")

    # Write the schema
    log.info(f"Creating schema for {module_name}")
    schema_path = path.join("./schema", module_name.lower() + ".json")

    with open(Path(schema_path), "w") as fh:
        fh.write("{\n")
        fh.write("    \"inputs\": {\n")
        fh.write("        \"file_options\": {\n")
        fh.write("            \"name\": \"File options\",\n")
        fh.write("            \"description\": \"Files needed to run the module\",\n")
        fh.write("            \"properties\": {\n")

        for idx, param in enumerate(param_list):
            fh.write(f"                \"{param}\": {{\n")

            if param in file_type_info:
                info = file_type_info[param]
                fh.write(f"                    \"name\": \"{info['name']}\",\n")
                fh.write(f"                    \"type\": \"{info['type']}\",\n")
                fh.write(f"                    \"pattern\": \"{info['pattern']}\",\n")
                fh.write(f"                    \"required\": \"true\",\n")
                fh.write(f"                    \"description\": \"{info['desc']}\"\n")
            else:
                fh.write(f"                    \"name\": \"UNKNOWN\",\n")
                fh.write(f"                    \"type\": \"UNKNOWN\",\n")
                fh.write(f"                    \"pattern\": \"UNKNOWN\",\n")
                fh.write(f"                    \"required\": true,\n")
                fh.write(f"                    \"description\": \"UNKNOWN\"\n")

            if idx == len(param_list) - 1:
                fh.write("                }\n")
            else:
                fh.write("                },\n")

        fh.write("            }\n")
        fh.write("        }\n")
        fh.write("    },\n")
        fh.write("    \"outputs\": [\n")
        fh.write("    ]\n")
        fh.write("}\n")

        log.warning("Make sure to add the test to the CI when complete!")


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
