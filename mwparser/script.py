"""
Updated on 2025-12
Created on 2025-11

@author: NewtCode Anna Burova
"""

from __future__ import annotations

import sys
import os
import shutil
from datetime import datetime, timedelta, timezone

import newtutils.console as NewtCons
import newtutils.files as NewtFiles
import newtutils.network as NewtNet

time_now = datetime.now(timezone.utc)
time_file_name = time_now.strftime('%Y-%m-%d-%H-%M-%S')
time_start = time_now - timedelta(days=0, hours=0)
time_start = time_start.strftime('%Y-%m-%dT%H:%M:%SZ')
time_end = time_now - timedelta(days=7, hours=0)
time_end = time_end.strftime('%Y-%m-%dT%H:%M:%SZ')

save_log = True

if save_log:
    class Tee:
        def __init__(self, a, b): self.a, self.b = a, b
        def write(self, s): self.a.write(s); self.b.write(s)
        def flush(self): self.a.flush(); self.b.flush()

    old = sys.stdout
    f = open(time_file_name+".txt", "a", encoding="utf-8", newline="\n")
    sys.stdout = Tee(old, f)
    sys.stderr = sys.stdout

dir_parser = os.path.dirname(os.path.realpath(__file__))
# print(dir_parser)  # D:\VS_Code\dev-parser-mediawiki\mwparser

dir_ = os.path.dirname(os.path.dirname(dir_parser))
# print(dir_)  # D:\VS_Code

# Add the project root directory to sys.path
sys.path.append(dir_)

must_location = os.path.join("D:\\", "VS_Code")

choose_config = "xxx.json"
check_config_folder = True

set_apcontinue = ""
check_apcontinue = False

namespace_types = {}

apnamespace_nr = 0
check_apnamespace = True

folder_raw_pages = os.path.join("data", "raw", "pages")
folder_lists = os.path.join("data", "lists")
folder_logs = os.path.join("data", "logs")
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


def select_from_input(
        select_dict: dict[str, str]
        ) -> str | None:
    """Select an option from input based on a provided dictionary."""

    # Display numbered list
    print("Available list:", len(select_dict))
    for nr, name in select_dict.items():
        print(f"{nr:>3}: {name}")
    print("999: Exit / Cancel")

    choice = 999
    # Loop until valid input
    while choice not in select_dict:
        try:
            choice = input("\nEnter number from list (999 to exit): ").strip()
            print(f"[INPUT]: {choice}")

            if choice == "999":
                NewtCons.error_msg(
                    "Selection cancelled.",
                    location="mwparser.select_from_input : choice = 999"
                )

            if not choice.isdigit():
                print("Invalid input. Please enter a number.")
                continue

            if choice in select_dict:
                print(f"Selected option: {select_dict[choice]}")
                print()
                return choice

            else:
                print("Number out of range. Try again.")

        except KeyboardInterrupt:
            NewtCons.error_msg(
                "Selection cancelled by user.",
                location="mwparser.select_from_input : KeyboardInterrupt"
            )

        except Exception as e:
            NewtCons.error_msg(
                f"Exception: {e}",
                location="mwparser.select_from_input : Exception"
            )


def get_blocked_list(
        ) -> set[str]:
    """Read blocked list from file and return as a set."""

    file_blocked_path = os.path.join(dir_, settings["FOLDER_LINK"], folder_lists, file_blocked)
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
    global namespace_types
    global apnamespace_nr

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

    required_keys = {"FOLDER_LINK", "BASE_URL"}
    check_dict_keys(settings, required_keys)

    config_type_list = {
        "1": "allpages",
        "2": "recentchanges",
    }

    config_type_nr = select_from_input(config_type_list)
    assert config_type_nr is not None

    config_type = config_type_list[config_type_nr]
    settings["config_type"] = config_type

    namespace_types = NewtFiles.read_json_from_file(
        os.path.join(dir_, settings["FOLDER_LINK"], "data", "schemas", "namespace_types.json")
    )
    # ensure the type checker knows namespace_types is a dict
    NewtCons.validate_input(
        namespace_types, dict,
        location="mwparser.read_config : namespace_types"
    )
    assert isinstance(namespace_types, dict)

    if config_type == "allpages":
        if check_apnamespace:
            apnamespace_nr = select_from_input(namespace_types)
            if apnamespace_nr is None:
                NewtCons.error_msg(
                    "No namespace selected, exiting",
                    location="mwparser.read_config.allpages : apnamespace_nr=None"
                )
            else:
                apnamespace_nr = int(apnamespace_nr)

        settings["file_name"] = os.path.join("allpages", f"{apnamespace_nr:05d}.csv")

    elif config_type == "recentchanges":
        settings["file_name"] = os.path.join("recentchanges.csv")

    elif config_type[0] == "pageids":
        required_keys = {"FOLDER_LINK", "BASE_URL", "pageids"}
        check_dict_keys(settings, required_keys)
        settings["prop"] = "revisions"
        settings["rvprop"] = "content"
        settings["rvslots"] = "main"

    else:
        NewtCons.error_msg(
            f"Unexpected config type: {config_type}",
            location="mwparser.read_config : config_type"
        )

    return settings


def set_args_for_url(
        apnamespace: int
        ) -> tuple:
    """Set headers and parameters for the URL request based on settings."""

    headers = {
        "User-Agent": "MyGuildWarsBot/1.1 (burova.anna+parser+bot@gmail.com)",
        "Accept-Encoding": "gzip",
    }

    params = {
        "action": "query",
        "format": "json",
        "maxlag": "1",
        "utf8": "true",
        "formatversion": "2",
    }

    if settings["config_type"] == "allpages":
        params.update({"list": "allpages"})
        params.update({"aplimit": "max"})
        params.update({"apnamespace": str(apnamespace)})

        if check_apcontinue:
            params.update({"apcontinue": set_apcontinue})

    elif settings["config_type"] == "recentchanges":
        params.update({"list": "recentchanges"})
        params.update({"rcnamespace": "*"})
        params.update({"rclimit": "max"})
        params.update({"rcstart": str(time_start)})
        params.update({"rcend": str(time_end)})

    elif settings["config_type"] == "pageids":
        params.update({"prop": settings["prop"]})
        params.update({"rvprop": settings["rvprop"]})
        params.update({"rvslots": settings["rvslots"]})

    return (headers, params)


def get_json_from_url(
        continue_param: str | None = None,
        continue_mw: str | None = None
        ) -> dict:
    """Fetch JSON data from a URL based on settings and save to file."""

    headers, params = args_for_url

    if settings["config_type"] == "allpages":
        if continue_param is not None:
            print(continue_param)

            if continue_param in blocked_set and continue_mw is not None:
                continue_param = continue_mw

            params.update({"apcontinue": continue_param})

    elif settings["config_type"] == "recentchanges":
        if continue_param is not None:
            print(continue_param)

            params.update({"rccontinue": continue_param})

    data_from_url = NewtNet.fetch_data_from_url(
        settings["BASE_URL"], params, headers,
        mode="alert", repeat_on_fail=False
    )
    print()

    # ensure the type checker knows settings is not None and is a dict
    if data_from_url is None:
        if continue_param is not None:
            file_blocked_path = os.path.join(dir_, settings["FOLDER_LINK"], folder_lists, file_blocked)
            NewtFiles.save_text_to_file(
                file_blocked_path,
                continue_param.replace(" ", "_"),
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
    allpages_list.append(["pageid", "title"])
    mw_apcontinue = ""
    for page in json_data_dict["query"]["allpages"]:
        required_keys_allpages = {"pageid", "ns", "title"}
        check_dict_keys(page, required_keys_allpages)

        if page["ns"] != apnamespace_nr:
            NewtCons.error_msg(
                f"Unexpected namespace value: {page['ns']} for page ID {page['pageid']}",
                f"Page: {page}",
                location="mwparser.restructure_json_allpages : page['ns']"
            )

        if page["title"].replace(" ", "_") not in blocked_set:
            mw_apcontinue = page["title"]
            left_part, sep_part, right_part = page["title"].partition(':')
            assert isinstance(namespace_types, dict)
            if sep_part and left_part in set(namespace_types.values()):
                mw_apcontinue = right_part.replace(" ", "_")

            allpages_list.append([
                f"{page['pageid']:010d}",
                page["title"],
            ])

    return (allpages_list, mw_apcontinue)


def restructure_json_recentchanges(
        json_data_dict: dict
        ) -> list[str]:
    """Process and save all pages from JSON data."""

    required_keys_json = {"query", "continue", "batchcomplete", "limits"}
    check_dict_keys(json_data_dict, required_keys_json)
    required_keys_query = {"recentchanges"}
    check_dict_keys(json_data_dict["query"], required_keys_query)

    recentchanges_list = []
    recentchanges_list.append(["timestamp", "pageid", "ns", "type", "title"])

    for page in json_data_dict["query"]["recentchanges"]:
        required_keys_recentchanges = {"type", "ns", "title", "pageid", "revid", "old_revid", "rcid", "timestamp"}
        check_dict_keys(page, required_keys_recentchanges)

        if str(page["ns"]) not in namespace_types:
            NewtCons.error_msg(
                f"Unexpected namespace value: {page['ns']} for page ID {page['title']}",
                f"Page: {page}",
                location="mwparser.restructure_json_recentchanges : page['ns']",
                stop=False
            )

        recentchanges_list.append([
            page['timestamp'],
            f"{page['pageid']:010d}",
            f"{page['ns']:03d}",
            f"{page['type']:>4}",
            page["title"],
        ])

    return recentchanges_list


def save_list_data(
        list_data_list: list[str],
        append: bool = True
        ) -> None:
    """Save the restructured list data to a file."""

    NewtFiles.save_csv_to_file(
        os.path.join(dir_, settings["FOLDER_LINK"], folder_lists, settings["file_name"]),
        list_data_list,
        append=append
    )
    print()


def loop_next_pages(
        json_data: dict,
        mw_apcontinue: str | None = None
        ) -> None:
    """Loop to fetch next pages based on the config type."""

    try:
        if settings["config_type"] == "allpages":
            while True:
                if "continue" not in json_data or not mw_apcontinue:
                    break

                required_keys = {"apcontinue", "continue"}
                check_dict_keys(json_data["continue"], required_keys)

                json_data = get_json_from_url(
                    continue_param = json_data["continue"]["apcontinue"].replace(" ", "_"),
                    continue_mw = mw_apcontinue
                )
                list_data, mw_apcontinue = restructure_json_allpages(json_data)

                save_list_data(list_data)

        elif settings["config_type"] == "recentchanges":
            while True:
                if "continue" not in json_data:
                    break

                required_keys = {"rccontinue", "continue"}
                check_dict_keys(json_data["continue"], required_keys)

                json_data = get_json_from_url(
                    continue_param = json_data["continue"]["rccontinue"]
                )

                list_data = restructure_json_recentchanges(json_data)

                save_list_data(list_data)

    except Exception as e:
        print(f"Script encountered an error: {e}")

    except SystemExit:
        print(f"SystemExit on fetching all pages")


def remove_duplicated_lines(
        ) -> None:
    """Remove duplicated lines from the recentchanges file."""

    file_path = os.path.join(dir_, settings["FOLDER_LINK"], folder_lists, settings["file_name"])
    lines = NewtFiles.read_csv_from_file(file_path)
    unique_lines = [list(t) for t in dict.fromkeys(map(tuple, lines))]

    NewtFiles.save_csv_to_file(
        file_path,
        unique_lines
    )
    print()


if __name__ == "__main__":
    check_location()
    settings = read_config()
    args_for_url = set_args_for_url(apnamespace_nr)
    blocked_set = get_blocked_list()
    json_data = get_json_from_url()

    if settings["config_type"] == "allpages":
        list_data, mw_apcontinue = restructure_json_allpages(json_data)
        save_list_data(list_data, False)
        loop_next_pages(json_data, mw_apcontinue)
        remove_duplicated_lines()

    elif settings["config_type"] == "recentchanges":
        list_data = restructure_json_recentchanges(json_data)
        save_list_data(list_data, False)
        loop_next_pages(json_data)
        remove_duplicated_lines()

    else:
        NewtCons.error_msg(
            f"Unexpected config type: {settings['config_type']}",
            location="mwparser.main : settings['config_type']"
        )

    print("=== END ===")

    if save_log:
        sys.stdout = old
        f.close()

        if settings["config_type"] == "allpages":
            file_target_name = f"{settings["config_type"]}-{apnamespace_nr:03d}.txt"
        else:
            file_target_name = f"{settings["config_type"]}.txt"

        path_target = os.path.join(dir_, settings["FOLDER_LINK"], folder_logs, file_target_name)
        shutil.move(time_file_name+".txt", path_target)
