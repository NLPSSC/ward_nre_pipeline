#!/usr/bin/env python

import sys
import yaml
from typing import Literal


def read_dev_entries(yaml_path, section: Literal["dev", "prod"]):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    entries = data.get(section, [])
    if len(entries) == 0:
        raise ValueError(f"No entries found in section '{section}'")
    return entries


if __name__ == "__main__":
    section = sys.argv[1] if len(sys.argv) > 1 else None
    if section not in ["dev", "prod"]:
        sys.stderr.write("Please provide a valid section: 'dev' or 'prod'\n")
        sys.exit(1)
    dev_entries = read_dev_entries(
        "/workspace/.devcontainer/nre_pipeline/requirements.grep.yml", section=section
    )
    sys.stdout.write("|".join(dev_entries))
