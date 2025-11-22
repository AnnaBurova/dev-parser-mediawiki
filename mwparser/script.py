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

must_location = os.path.join("D:\\", "VS_Code")

choose_config = "allpages-xxx.json"
check_config_folder = True

set_apcontinue = ""
check_apcontinue = False

folder_raw_pages = os.path.join("data", "raw", "pages")
folder_lists = os.path.join("data", "lists")
file_allpages_list = "allpages-list.csv"
file_blocked = "blocked.txt"


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
        expected: set[str],
        ) -> None:
    """Check if the dictionary has the expected keys."""

    data_keys = set(data.keys())
    expected_keys = set(expected)
    missing_keys = expected_keys - data_keys
    extra_keys = data_keys - expected_keys

    if missing_keys or extra_keys:
        NewtCons.error_msg(
            f"Data keys: {', '.join(sorted(data_keys))}",
            f"Missing keys: {', '.join(sorted(missing_keys))}",
            f"Unexpected keys: {', '.join(sorted(extra_keys))}",
            location="mwparser.check_dict_keys",
            stop=False
        )


def get_blocked_list(
        ) -> set[str]:
    """Read blocked list from file and return as a set."""

    file_blocked_path = os.path.join(settings["FOLDER_LINK"], folder_lists, file_blocked)
    blocked_list = NewtFiles.read_text_from_file(file_blocked_path)
    print()

    blocked_set = set()
    for line in blocked_list.splitlines():
        line = line.strip()
        if line:
            blocked_set.add(line)

    return blocked_set


def read_config(
        ) -> dict:
    """Read configuration from a selected JSON file."""

    global choose_config

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

    config_type = choose_config.split("-")

    if config_type[0] == "allpages":
        required_keys = {"FOLDER_LINK", "BASE_URL"}
        check_dict_keys(settings, required_keys)
        settings["list"] = "allpages"
        settings["aplimit"] = "max"
        settings["config_type"] = "allpages"

    elif config_type[0] == "pageids":
        required_keys = {"FOLDER_LINK", "BASE_URL", "pageids"}
        check_dict_keys(settings, required_keys)
        settings["prop"] = "revisions"
        settings["rvprop"] = "content"
        settings["rvslots"] = "main"
        settings["config_type"] = "pageids"

    else:
        NewtCons.error_msg(
            f"Unexpected config type: {config_type[0]}",
            location="mwparser.read_config : config_type"
        )

    return settings


def set_args_for_url(
        ) -> tuple:
    """Set arguments for URL request based on settings."""

    headers = {
        "User-Agent": "MyGuildWarsBot/1.1 (burova.anna+parser+bot@gmail.com)",
        "Accept-Encoding": "gzip",
    }

    params = {
        "action": "query",
        "format": "json",
        "maxlag": "1",
    }

    if settings["config_type"] == "allpages":
        params.update({"list": settings["list"]})
        params.update({"aplimit": settings["aplimit"]})

        if check_apcontinue:
            params.update({"apcontinue": set_apcontinue})

    elif settings["config_type"] == "pageids":
        params.update({"prop": settings["prop"]})
        params.update({"rvprop": settings["rvprop"]})
        params.update({"rvslots": settings["rvslots"]})

    return (headers, params)


def get_json_from_url(
        apcontinue: str | None = None,
        mw_apcontinue: str | None = None
        ) -> dict:
    """Fetch JSON data from a URL based on settings and save to file."""

    headers, params = args_for_url

    if apcontinue is not None:
        if apcontinue in blocked_set and mw_apcontinue is not None:
            apcontinue = mw_apcontinue

        print(apcontinue)

        params.update({"apcontinue": apcontinue})

    data_from_url = NewtNet.fetch_data_from_url(
        settings["BASE_URL"], params, headers,
        mode="alert", repeat_on_fail=False
    )
    print()

    # ensure the type checker knows settings is not None and is a dict
    if data_from_url is None:
        if apcontinue is not None:
            file_blocked_path = os.path.join(settings["FOLDER_LINK"], folder_lists, file_blocked)
            NewtFiles.save_text_to_file(
                file_blocked_path,
                apcontinue,
                append=True
            )

        NewtCons.error_msg(
            "Failed to read config JSON, exiting",
            location="mwparser.get_json_from_url : data_from_url=None"
        )
    # ensure the type checker knows choose_config is not None
    assert data_from_url is not None

    json_from_url = NewtFiles.convert_str_to_json(data_from_url)

    NewtCons.validate_input(
        json_from_url, dict,
        location="mwparser.get_json_from_url : json_from_url != dict"
    )
    assert isinstance(json_from_url, dict)

    # NewtFiles.save_json_to_file(
    #     os.path.join(dir_, settings["FOLDER_LINK"], folder_lists, "allpages-last-result.json"),
    #     json_from_url,
    # )
    # print()

    return json_from_url


def restructure_json_allpages(
        json_data_dict: dict
        ) -> tuple[list[str], str]:
    """Process and save all pages from JSON data."""

    required_keys_json = {"query", "continue", "batchcomplete", "limits"}
    check_dict_keys(json_data_dict, required_keys_json)
    required_keys_query = {"allpages"}
    check_dict_keys(json_data_dict["query"], required_keys_query)

    allpages_list = []
    mw_apcontinue = ""
    for page in json_data_dict["query"]["allpages"]:
        required_keys_allpages = {"pageid", "ns", "title"}
        check_dict_keys(page, required_keys_allpages)

        if page["ns"] != 0:
            NewtCons.error_msg(
                f"Unexpected namespace value: {page['ns']} for page ID {page['pageid']}",
                location="mwparser.______ : page['ns']"
            )

        allpages_list.append(f"{page['pageid']:010d};{page['title']}")

        if page["title"].replace(" ", "_") not in blocked_set:
            mw_apcontinue = page["title"].replace(" ", "_")

    return (allpages_list, mw_apcontinue)


def save_list_data(
        list_data_str: list[str],
        append: bool = True
        ) -> None:
    """Save the restructured list data to a file."""

    NewtFiles.save_text_to_file(
        os.path.join(dir_, settings["FOLDER_LINK"], folder_lists, file_allpages_list),
        "\n".join(list_data_str),
        append=append
    )
    print()


if __name__ == "__main__":
    check_location()
    settings = read_config()
    args_for_url = set_args_for_url()
    blocked_set = get_blocked_list()
    json_data = get_json_from_url()
    list_data, mw_apcontinue = restructure_json_allpages(json_data)
    save_list_data(list_data, False)

    try:
        while True:
            if "continue" not in json_data or not mw_apcontinue:
                break

            required_keys = {"apcontinue", "continue"}
            check_dict_keys(json_data["continue"], required_keys)
            json_data = get_json_from_url(
                json_data["continue"]["apcontinue"].replace(" ", "_"),
                mw_apcontinue
            )
            list_data, mw_apcontinue = restructure_json_allpages(json_data)
            save_list_data(list_data)

    except Exception as e:
        print(f"Script encountered an error: {e}")
    except SystemExit:
        print(f"SystemExit on fetching all pages")

    print("=== END ===")
