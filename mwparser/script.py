"""
Created on 2025-11

@author: NewtCode Anna Burova
"""

from __future__ import annotations

import sys
import os
import newtutils.console as NewtCons
import newtutils.files as NewtFiles
import newtutils.network as NewtNet

dir_parser = os.path.dirname(os.path.realpath(__file__))
# print(dir_parser)  # D:\VS_Code\dev-parser-mediawiki\mwparser

dir_ = os.path.dirname(os.path.dirname(dir_parser))
# print(dir_)  # D:\VS_Code

# Add the project root directory to sys.path
sys.path.append(dir_)

choose_config = "allpages-xxx.json"
must_location = os.path.join("D:\\", "VS_Code")
check_config_folder = True


def check_location(
        ) -> None:
    """Check if the provided location exists and is a directory."""

    if dir_ == must_location:
        print("=== START ===")
    else:
        NewtCons.error_msg(
            f"Something wrong, check folder: {dir_}",
            location="mwparser.check_location"
        )


def check_dict_keys(
        data: dict,
        expected: tuple,
        ) -> None:
    """Check if the dictionary has the expected keys."""

    data_keys = set(data.keys())
    expected_keys = set(expected)
    missing_keys = expected_keys - data_keys
    extra_keys = data_keys - expected_keys

    if missing_keys or extra_keys:
        NewtCons.error_msg(
            f"Missing keys: {', '.join(missing_keys)}",
            f"Unexpected keys: {', '.join(extra_keys)}",
            location="mwparser.check_dict_keys"
        )


def read_config(
        ) -> dict:
    """Read configuration from a selected JSON file."""

    if check_config_folder:
        choose_config = NewtFiles.choose_file_from_folder(os.path.join(dir_parser, "configs"))

    if not choose_config:
        NewtCons.error_msg(
            "No config selected, exiting",
            location="mwparser.read_config : choose_config=None"
        )
    # ensure the type checker knows choose_config is not None
    assert choose_config is not None

    config_path = os.path.join(dir_parser, "configs", choose_config)
    settings = NewtFiles.read_json_from_file(config_path)
    print()

    # ensure the type checker knows settings is a dict
    NewtCons.validate_input(
        settings, dict,
        location="mwparser.read_config : settings"
        )
    assert isinstance(settings, dict)

    required_keys = ("FOLDER_LINK", "BASE_URL", "action", "list", "aplimit")
    check_dict_keys(settings, required_keys)

    return settings


def get_json_from_url(
        settings: dict
        ) -> dict:
    """Fetch JSON data from a URL based on settings and save to file."""

    headers = {
        "User-Agent": "MyGuildWarsBot/1.1 (burova.anna+parser+bot@gmail.com)",
        "Accept-Encoding": "gzip",
    }
    params = {
        "action": settings["action"],
        "list": settings["list"],
        "aplimit": settings["aplimit"],
        "format": "json",
        "maxlag": "1",
        # "apcontinue": "Grawl",
    }
    BASE_URL = settings["BASE_URL"]
    FOLDER_LINK = os.path.join(settings["FOLDER_LINK"], "data", "raw", "pages")

    data_from_url = NewtNet.fetch_data_from_url(BASE_URL, params, headers, mode="alert")
    print()

    # ensure the type checker knows settings is not None and is a dict
    if data_from_url is None:
        NewtCons.error_msg(
            "Failed to read config JSON, exiting",
            location="mwparser.get_json_from_url : data_from_url=None"
        )
    # ensure the type checker knows choose_config is not None
    assert data_from_url is not None

    json_from_url = NewtFiles.convert_str_to_json(data_from_url)

    # ensure the type checker knows settings is not None and is a dict
    if json_from_url is None:
        NewtCons.error_msg(
            "Failed to read config JSON, exiting",
            location="mwparser.get_json_from_url : json_from_url=None"
        )
    # ensure the type checker knows json_from_url is not None
    assert json_from_url is not None

    # ensure the type checker knows json_from_url is a dict
    if not isinstance(json_from_url, dict):
        NewtCons.error_msg(
            "Expected dict from JSON conversion, exiting",
            location="mwparser.get_json_from_url : json_from_url is not dict"
        )
    assert isinstance(json_from_url, dict)

    NewtFiles.save_json_to_file(
        os.path.join(dir_, FOLDER_LINK, "allpages-sample.json"),
        json_from_url,
    )
    print()

    return json_from_url

if __name__ == "__main__":
    check_location()
    settings = read_config()
    json_data = get_json_from_url(settings)

    print("=== END ===")
