"""
Created on 2025-11

@author: NewtCode Anna Burova
"""

from __future__ import annotations

import sys
import os
import newtutils.console as NewtCons
import newtutils.files as NewtFiles

dir_parser = os.path.dirname(os.path.realpath(__file__))
# print(dir_parser)  # D:\VS_Code\dev-parser-mediawiki\mwparser

dir_ = os.path.dirname(os.path.dirname(dir_parser))
# print(dir_)  # D:\VS_Code

# Add the project root directory to sys.path
sys.path.append(dir_)

choose_config = "allpages-xxx.json"
must_location = os.path.join("D:\\", "VS_Code")


def check_location(
        ) -> None:
    """Check if the provided location exists and is a directory."""

    if dir_ == must_location:
        print("=== START ===")
    else:
        NewtCons.error_msg(
            f"Something wrong, check folder: {dir_}",
            location="mwparser.allpages.check_location"
        )


def read_config(
        ) -> list | dict:
    """Read configuration from a selected JSON file."""

    choose_config = NewtFiles.choose_file_from_folder(os.path.join(dir_parser, "configs"))

    if not choose_config:
        NewtCons.error_msg(
            "No config selected, exiting",
            location="mwparser.allpages.read_config : choose_config=None"
        )
    # ensure the type checker knows choose_config is not None
    assert choose_config is not None

    config_path = os.path.join(dir_parser, "configs", choose_config)
    settings = NewtFiles.read_json_from_file(config_path)

    # ensure the type checker knows settings is not None and is a dict
    if settings is None:
        NewtCons.error_msg(
            "Failed to read config JSON, exiting",
            location="mwparser.allpages.read_config : settings=None"
        )

    return settings


if __name__ == "__main__":
    check_location()
    settings = read_config()

    print("=== END ===")
