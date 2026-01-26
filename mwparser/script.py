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
        def flush(self):
            self.a.flush()
            try:
                self.b.flush()
            except ValueError:
                pass  # File already closed

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

settings_index_start = 0

folder_raw_pages = os.path.join("data", "raw", "pages")
folder_raw_redirect = os.path.join("data", "raw", "redirect")
folder_raw_removed = os.path.join("data", "raw", "removed")
folder_raw_images = os.path.join("data", "raw", "images")
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


def check_todo(
        ) -> None:

    todo_list = []
    folder_config = os.path.join(dir_parser, "configs")
    for file in os.listdir(folder_config):
        if not os.path.isfile(os.path.join(folder_config, file)):
            continue

        if file == "xxx.json":
            continue

        if file.endswith(".json"):
            config_path = os.path.join(folder_config, file)
            settings = NewtFiles.read_json_from_file(config_path)

            NewtCons.validate_input(
                settings, dict,
                location="mwparser.check_todo : settings"
            )
            assert isinstance(settings, dict)

            namespace_types = os.path.join(dir_, settings["FOLDER_LINK"], "data", "schemas", "namespace_types.json")
            if not os.path.isfile(namespace_types):
                NewtCons.error_msg(
                    f"Missing namespace_types.json for config: {file}",
                    location="mwparser.check_todo : namespace_types.json missing"
                )
            n_types = NewtFiles.read_json_from_file(namespace_types)
            assert isinstance(n_types, dict)

            folder_logs = os.path.join(dir_, settings["FOLDER_LINK"], "data", "logs")

            for n_type in n_types.keys():
                file_ap = os.path.join(folder_logs, f"allpages-{int(n_type):03d}.txt")
                if not os.path.isfile(file_ap):
                    todo_list.append(f"Proj: {file} missing allpages file: {n_type}")

            for n_type in n_types.keys():
                file_pi = os.path.join(folder_logs, f"pageids-{int(n_type):03d}.txt")
                if not os.path.isfile(file_pi):
                    todo_list.append(f"Proj: {file} missing pageids file: {n_type}")

            file_rc = os.path.join(folder_logs, "recentchanges.txt")
            if not os.path.isfile(file_rc):
                todo_list.append(f"Proj: {file} missing file: recentchanges.txt")

            file_pr = os.path.join(folder_logs, "pagesrecent.txt")
            if not os.path.isfile(file_pr):
                todo_list.append(f"Proj: {file} missing file: pagesrecent.txt")

    todo_list.reverse()
    print()
    print("=== TODO LIST ===")
    for todo in todo_list:
        print(todo)
    print()


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
        "2": "pageids",
        "3": "recentchanges",
        "4": "pagesrecent",
        "5": "savefiles",
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

    if config_type in (
        "allpages",
        "pageids",
        "savefiles",
    ):
        if check_apnamespace:
            apnamespace_nr = select_from_input(namespace_types)
            if apnamespace_nr is None:
                NewtCons.error_msg(
                    "No namespace selected, exiting",
                    location="mwparser.read_config.allpages : apnamespace_nr=None"
                )
            else:
                apnamespace_nr = int(apnamespace_nr)

    if config_type == "allpages":
        settings["file_name"] = os.path.join("allpages", f"{apnamespace_nr:05d}.csv")

    elif config_type == "recentchanges":
        settings["file_name"] = os.path.join("recentchanges.csv")

    elif config_type == "pageids":
        file_allpages = os.path.join(dir_, settings["FOLDER_LINK"], folder_lists, "allpages", f"{apnamespace_nr:05d}.csv")
        list_allpages = NewtFiles.read_csv_from_file(file_allpages)

        # skip header
        settings["allpages_ids"] = sorted([int(row[0]) for row in list_allpages[1:]])
        settings["index_start"] = settings_index_start

    elif config_type == "pagesrecent":
        file_recentchanges = os.path.join(dir_, settings["FOLDER_LINK"], folder_lists, "recentchanges.csv")
        list_recentchanges = NewtFiles.read_csv_from_file(file_recentchanges)
        settings["recentchanges"] = sorted(list(set([int(row[1]) for row in list_recentchanges[1:] if int(row[1]) > 0])))
        settings["index_start"] = settings_index_start

    elif config_type == "savefiles":
        file_allpages = os.path.join(dir_, settings["FOLDER_LINK"], folder_lists, "allpages", f"{apnamespace_nr:05d}.csv")
        list_allpages = NewtFiles.read_csv_from_file(file_allpages)

        # skip header
        settings["allpages_titles"] = sorted([str(row[1]) for row in list_allpages[1:]])
        settings["index_start"] = settings_index_start

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
        "maxlag": "2",
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
        params.update({"prop": "revisions"})
        params.update({"rvprop": "content"})
        params.update({"rvslots": "*"})

    elif settings["config_type"] == "pagesrecent":
        params.update({"prop": "revisions"})
        params.update({"rvprop": "content"})
        params.update({"rvslots": "*"})

    elif settings["config_type"] == "savefiles":
        params.update({"maxlag": "5"})
        params.update({"prop": "imageinfo"})
        params.update({"iiprop": "url"})

    return (headers, params)


def get_json_from_url(
        continue_param: str | None = None,
        continue_mw: str | None = None
        ) -> dict:
    """Fetch JSON data from a URL based on settings and save to file."""

    headers, params = args_for_url

    if settings["config_type"] == "allpages":
        if continue_param is not None:
            if continue_param in blocked_set and continue_mw is not None:
                continue_param = continue_mw

            print(continue_param)
            params.update({"apcontinue": continue_param})

    elif settings["config_type"] == "recentchanges":
        if continue_param is not None:
            print(continue_param)
            params.update({"rccontinue": continue_param})

    elif settings["config_type"] == "pageids":
        index_start = settings["index_start"]
        # max 50 pages per MediaWiki Settings for no admin users
        index_max = 50

        if len(settings['allpages_ids']) == 0:
            print("No pages to process.")
            return {}

        if len(settings["allpages_ids"]) < index_start:
            print("No more pages to process.")
            return {}

        index_end = index_start + index_max
        params.update({"pageids": '|'.join(
            map(str, settings["allpages_ids"][index_start:index_end])
        )})
        settings["index_start"] = index_end

        print()
        print(f"Processing page IDs from index {index_start} to {index_end - 1}")
        print(f"Progress current page: {index_start / index_max}")
        print(f"Progress max pages: {len(settings['allpages_ids']) / index_max}")
        print()

    elif settings["config_type"] == "pagesrecent":
        index_start = settings["index_start"]
        # max 50 pages per MediaWiki Settings for no admin users
        index_max = 50

        if len(settings['recentchanges']) == 0:
            print("No pages to process.")
            return {}

        if len(settings["recentchanges"]) < index_start:
            print("No more pages to process.")
            return {}

        index_end = index_start + index_max
        params.update({"pageids": '|'.join(
            map(str, settings["recentchanges"][index_start:index_end])
        )})
        settings["index_start"] = index_end

        print()
        print(f"Processing page IDs from index {index_start} to {index_end - 1}")
        print(f"Progress current page: {index_start / index_max}")
        print(f"Progress max pages: {len(settings['recentchanges']) / index_max}")
        print()

    elif settings["config_type"] == "savefiles":
        index_start = settings["index_start"]
        # it must be 25 titles max
        index_max = 25

        if len(settings['allpages_titles']) == 0:
            print("No images to process.")
            return {}

        if len(settings["allpages_titles"]) < index_start:
            print("No more images to process.")
            return {}

        index_end = index_start + index_max
        params.update({"titles": '|'.join(
            map(str, settings["allpages_titles"][index_start:index_end])
        )})
        settings["index_start"] = index_end

        print()
        print(f"Processing images IDs from index {index_start} to {index_end - 1}")
        print(f"Progress current page: {index_start / index_max}")
        print(f"Progress max pages: {len(settings['allpages_titles']) / index_max}")
        print()

    data_from_url = NewtNet.fetch_data_from_url(
        settings["BASE_URL"], params, headers,
        mode="manual", repeat_on_fail=True
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

    if len(data_from_url) > 500000:
        # Need to try to split request into two pieces, to be sure it will return all data

        # PART 1 -------
        index_split_end = index_end - 25
        params.update({"titles": '|'.join(
            map(str, settings["allpages_titles"][index_start:index_split_end])
        )})

        data_from_url = NewtNet.fetch_data_from_url(
            settings["BASE_URL"], params, headers,
            mode="manual", repeat_on_fail=True
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

        # PART 2 -------
        index_split_start = index_start + 25
        params.update({"titles": '|'.join(
            map(str, settings["allpages_titles"][index_split_start:index_end])
        )})

        data_from_url = NewtNet.fetch_data_from_url(
            settings["BASE_URL"], params, headers,
            mode="manual", repeat_on_fail=True
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

        # END SPLIT -------

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

    if "continue" in json_data_dict:
        required_keys_json = {"query", "continue", "batchcomplete", "limits"}
        check_dict_keys(json_data_dict, required_keys_json)
    else:
        required_keys_json = {"query", "batchcomplete", "limits"}
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


    if "continue" in json_data_dict:
        required_keys_json = {"query", "continue", "batchcomplete", "limits"}
        check_dict_keys(json_data_dict, required_keys_json)
    else:
        required_keys_json = {"query", "batchcomplete", "limits"}
        check_dict_keys(json_data_dict, required_keys_json)

    required_keys_query = {"recentchanges"}
    check_dict_keys(json_data_dict["query"], required_keys_query)

    recentchanges_list = []
    recentchanges_list.append(["timestamp", "pageid", "ns", "type", "title"])

    for page in json_data_dict["query"]["recentchanges"]:
        if "pageid" not in page:
            NewtCons.error_msg(
                "No pageid for page log",
                f"Page: {page}",
                location="mwparser.restructure_json_recentchanges : 'pageid' not in page",
                stop=False
            )
            continue

        required_keys_recentchanges = {"type", "ns", "title", "pageid", "revid", "old_revid", "rcid", "timestamp"}
        check_dict_keys(page, required_keys_recentchanges)

        if str(page["ns"]) not in namespace_types:
            NewtCons.error_msg(
                f"Unexpected namespace value: {page['ns']} for page ID {page['title']}",
                f"Page: {page}",
                location="mwparser.restructure_json_recentchanges : page['ns']",
                stop=False
            )

        if page['pageid'] == 0:
            continue

        recentchanges_list.append([
            page['timestamp'],
            f"{page['pageid']:010d}",
            f"{page['ns']:03d}",
            f"{page['type']:>4}",
            page["title"],
        ])

    return recentchanges_list


def restructure_json_pageids(
        json_data_dict: dict
        ) -> None:

    global namespace_types
    global apnamespace_nr
    assert isinstance(namespace_types, dict)

    file_blocked_path = os.path.join(dir_, settings["FOLDER_LINK"], folder_lists, file_blocked)

    if "query" not in json_data_dict:
        return

    required_keys_json = {"query", "batchcomplete"}
    check_dict_keys(json_data_dict, required_keys_json)
    required_keys_query = {"pages"}
    check_dict_keys(json_data_dict["query"], required_keys_query)

    for page in json_data_dict["query"]["pages"]:
        if settings["config_type"] in (
                "pageids",
                "pagesrecent",
                ):
            if "missing" in page:
                NewtCons.error_msg(
                    f"Page ID {page['pageid']} data is missing",
                    f"Page: {page}",
                    location="mwparser.restructure_json_pageids.pagesrecent : 'missing' in page",
                    stop=False
                )
                for missing_folder in (folder_raw_pages, folder_raw_redirect):
                    for missing_apname in namespace_types.keys():
                        missing_file = os.path.join(dir_, settings["FOLDER_LINK"], missing_folder, f"{int(missing_apname):05d}", f"{page['pageid']:010d}.txt")
                        missing_target = os.path.join(dir_, settings["FOLDER_LINK"], folder_raw_removed, f"{int(missing_apname):05d}-{page['pageid']:010d}.txt")
                        if NewtFiles._check_file_exists(missing_file):
                            NewtFiles._ensure_dir_exists(missing_target)
                            shutil.move(missing_file, missing_target)
                continue

        required_keys_page = {"pageid", "ns", "title", "revisions"}
        check_dict_keys(page, required_keys_page)

        if settings["config_type"] == "pagesrecent":
            apnamespace_nr = page["ns"]

        if page["ns"] != apnamespace_nr:
            NewtCons.error_msg(
                f"Unexpected namespace value: {page['ns']} for page ID {page['pageid']}",
                f"Page: {page}",
                location="mwparser.restructure_json_pageids : page['ns']"
            )

        if page['title'].replace(" ", "_") in blocked_set:
            continue

        folder_pages = folder_raw_pages

        text_for_file = ""
        text_for_file += f"Namespace ::: {apnamespace_nr} ::: {namespace_types[str(apnamespace_nr)]}\n"
        text_for_file += f"Page ID   ::: {page['pageid']}\n"
        text_for_file += f"Title     ::: {page['title']}\n\n"

        for revision in page["revisions"]:
            required_keys_revision = {"slots"}
            check_dict_keys(revision, required_keys_revision)
            required_keys_main = {"main"}
            check_dict_keys(revision["slots"], required_keys_main)
            required_keys_content = {"contentmodel", "contentformat", "content"}
            check_dict_keys(revision["slots"]["main"], required_keys_content)

            if revision["slots"]["main"]["contentmodel"] != "wikitext":
                NewtCons.error_msg(
                    f"Unexpected Contentmodel : {revision["slots"]["main"]["contentmodel"]}",
                    f"Title: {page['title']}",
                    f"Page: {page['pageid']}",
                    location="mwparser.restructure_json_pageids : revision[slots][main][contentmodel]",
                    stop=False
                )
                NewtFiles.save_text_to_file(
                    file_blocked_path,
                    page['title'].replace(" ", "_"),
                    append=True
                )
                continue

            if revision["slots"]["main"]["contentformat"] != "text/x-wiki":
                NewtCons.error_msg(
                    f"Unexpected Contentformat : {revision["slots"]["main"]["contentformat"]}",
                    f"Title: {page['title']}",
                    f"Page: {page['pageid']}",
                    location="mwparser.restructure_json_pageids : revision[slots][main][contentformat]"
                )
                NewtFiles.save_text_to_file(
                    file_blocked_path,
                    page['title'].replace(" ", "_"),
                    append=True
                )
                continue

            if len(revision["slots"]["main"]["content"]) < 6:
                folder_pages = folder_raw_removed

            if revision["slots"]["main"]["content"].lower().startswith("#redirect"):
                folder_pages = folder_raw_redirect

            text_for_file += f"{revision["slots"]["main"]["content"]}\n\n"

        text_for_file += "=== END ===\n"

        file_pageid = os.path.join(dir_, settings["FOLDER_LINK"], folder_pages, f"{apnamespace_nr:05d}", f"{page['pageid']:010d}.txt")
        NewtFiles.save_text_to_file(
            file_pageid,
            text_for_file
        )


def restructure_json_savefiles(
        json_data_dict: dict
        ) -> None:

    if "query" not in json_data_dict:
        return

    required_keys_json = {"batchcomplete", "query"}
    check_dict_keys(json_data_dict, required_keys_json)
    required_keys_query = {"pages"}
    check_dict_keys(json_data_dict["query"], required_keys_query)

    for image_info in json_data_dict["query"]["pages"]:
        if "imageinfo" not in image_info:
            continue

        required_keys_image = {"pageid", "ns", "title", "imagerepository", "imageinfo"}
        check_dict_keys(image_info, required_keys_image)

        if len(image_info["imageinfo"]) != 1:
            NewtCons.error_msg(
                f"Unexpected imageinfo length: {len(image_info['imageinfo'])} for image title: {image_info['title']}",
                location="mwparser.get_image_from_pages : len(image_info['imageinfo']) != 1"
            )
            continue

        required_keys_imageinfo = {"url", "descriptionurl", "descriptionshorturl"}
        check_dict_keys(image_info["imageinfo"][0], required_keys_imageinfo)

        url_filename = os.path.basename(image_info["imageinfo"][0]["url"])
        filename = f"{image_info['pageid']:010d}-{url_filename}"
        img_file_path = os.path.join(dir_, settings["FOLDER_LINK"], folder_raw_images, filename)

        i = 0
        while True:
            i += 1
            if NewtNet.download_file_from_url(
                image_info["imageinfo"][0]["url"],
                img_file_path,
                repeat_on_fail=False
            ):
                break

            if i >= 5:
                NewtCons.error_msg(
                    f"Failed to download image after {i} attempts: {image_info['imageinfo'][0]['url']}",
                    location="mwparser.restructure_json_savefiles : download_file_from_url",
                    stop=False
                )
                missed_files_log = os.path.join(dir_, settings["FOLDER_LINK"], folder_lists, "missed_files.txt")
                NewtFiles.save_text_to_file(
                    missed_files_log,
                    f"{image_info["imageinfo"][0]["url"]} > {img_file_path}",
                    append=True
                )
                break
        print()


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

        elif settings["config_type"] == "pageids":
            while True:
                if json_data == {}:
                    break

                restructure_json_pageids(json_data)
                json_data = get_json_from_url()

        elif settings["config_type"] == "pagesrecent":
            while True:
                if json_data == {}:
                    break

                restructure_json_pageids(json_data)
                json_data = get_json_from_url()

        elif settings["config_type"] == "savefiles":
            while True:
                if json_data == {}:
                    break

                restructure_json_savefiles(json_data)
                json_data = get_json_from_url()

    except Exception as e:
        print(f"Script encountered an error: {e}")

    except SystemExit:
        print("SystemExit on fetching all pages")


def remove_duplicated_lines(
        ) -> None:
    """Remove duplicated lines from the recentchanges file."""

    file_path = os.path.join(dir_, settings["FOLDER_LINK"], folder_lists, settings["file_name"])
    lines = NewtFiles.read_csv_from_file(file_path)

    # Separate header from data
    header = lines[0] if lines else []
    data_lines = lines[1:] if len(lines) > 1 else []

    # Ensure header does not exist in data_lines
    data_lines = [line for line in data_lines if line != header]

    # Remove duplicates from data only
    unique_lines = [list(t) for t in dict.fromkeys(map(tuple, data_lines))]
    unique_lines.sort()

    # Prepend header back
    unique_lines = [header] + unique_lines

    NewtFiles.save_csv_to_file(
        file_path,
        unique_lines
    )
    print()


if __name__ == "__main__":
    check_location()
    check_todo()
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

    elif settings["config_type"] in (
            "pageids",
            "pagesrecent",
            "savefiles",
            ):
        loop_next_pages(json_data)

    else:
        NewtCons.error_msg(
            f"Unexpected config type: {settings['config_type']}",
            location="mwparser.main : settings['config_type']"
        )

    print("=== END ===", end="")

    if save_log:
        sys.stdout = old
        f.close()

        print()

        if settings["config_type"] in (
                "allpages",
                "pageids",
                ):
            file_target_name = f"{settings["config_type"]}-{apnamespace_nr:03d}.txt"
        else:
            file_target_name = f"{settings["config_type"]}.txt"

        path_target = os.path.join(dir_, settings["FOLDER_LINK"], folder_logs, file_target_name)

        print("Log moved to", path_target)

        NewtFiles._ensure_dir_exists(path_target)
        shutil.move(time_file_name+".txt", path_target)

        print()
