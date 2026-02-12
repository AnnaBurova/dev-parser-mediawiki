"""
Updated on 2026-02
Created on 2025-11

@author: NewtCode Anna Burova
"""

from __future__ import annotations

import sys
import os
import shutil
from datetime import datetime, timedelta, timezone

import newtutils.console as NewtCons
import newtutils.utility as NewtUtil
import newtutils.files as NewtFiles
import newtutils.network as NewtNet

DIR_PROJECT = os.path.dirname(os.path.realpath(__file__))
# print(DIR_PROJECT)  # D:\VS_Code\dev-parser-mediawiki\mwparser

DIR_GLOBAL = os.path.dirname(os.path.dirname(DIR_PROJECT))
# print(DIR_GLOBAL)  # D:\VS_Code

# Add the project root directory to sys.path
sys.path.append(DIR_GLOBAL)

MUST_LOCATION = os.path.join("D:\\", "VS_Code")

BACK_IN_TIME_DAYS = 7
TIME_NOW = datetime.now(timezone.utc)
time_start = TIME_NOW - timedelta(days=0, hours=0)
time_start = time_start.strftime('%Y-%m-%dT%H:%M:%SZ')
time_end = TIME_NOW - timedelta(days=BACK_IN_TIME_DAYS, hours=0)
time_end = time_end.strftime('%Y-%m-%dT%H:%M:%SZ')

FOLDER_RAW_PAGES = os.path.join("data", "raw", "pages")
FOLDER_RAW_REDIRECT = os.path.join("data", "raw", "redirect")
FOLDER_RAW_REMOVED = os.path.join("data", "raw", "removed")
FOLDER_RAW_IMAGES = os.path.join("data", "raw", "images")
FOLDER_LISTS = os.path.join("data", "lists")
FOLDER_LOGS = os.path.join("data", "logs")
FILE_NAMESPACES = os.path.join("data", "schemas", "namespace_types.json")
FILE_BLOCKED = "blocked.txt"

# Extended functionality in read_config()
FOLDER_CONFIG_CHECK = False
FOLDER_CONFIG_CHECK = True
# If FOLDER_CONFIG_CHECK is False, set the config file name here
# File must be in configs folder
file_config_set = "xxx.json"

WIKI_DATA_TYPE_DICT = {
    "1": "allpages",
    "2": "pageids",
    "3": "recentchanges",
    "4": "pagesrecent",
    "5": "savefiles",
}

# Extended functionality in read_config()
WIKI_DATA_TYPE_CHECK = False
WIKI_DATA_TYPE_CHECK = True
# If WIKI_DATA_TYPE_CHECK is False, set the wiki data type here
wiki_data_type_set = WIKI_DATA_TYPE_DICT["1"]

namespace_types_set = {}
# Extended functionality in read_config()
NAMESPACE_NR_CHECK = False
NAMESPACE_NR_CHECK = True
# If NAMESPACE_NR_CHECK is False, set namespace number here
namespace_nr_set = 0

# Extended functionality in prep_headers_params_for_url()
APCONTINUE_CHECK = True
APCONTINUE_CHECK = False
# If APCONTINUE_CHECK is True, set apcontinue value here
APCONTINUE_PARAM = ""

SAVE_LOG = True
SAVE_LOG = False

if SAVE_LOG:
    SETUP_LOGGING_DATA = NewtFiles.setup_logging(DIR_GLOBAL)


def check_todo(
        ) -> list[tuple[str, str, str]]:
    """ Check for missing log files based on existing config files and return a list of tasks to do. """

    todo_list = []
    path_config = os.path.join(DIR_PROJECT, "configs")
    for file in os.listdir(path_config):
        # Skip if it's not a file (e.g., directory)
        if not os.path.isfile(os.path.join(path_config, file)):
            continue

        # Skip specific config example file
        if file == "xxx.json":
            continue

        # Skip non-config files
        if not file.endswith(".json"):
            NewtCons.error_msg(
                f"Found non-config file: {file}", stop=False,
                location="mwparser.check_todo : non-config file"
            )
            continue

        # Get settings from config file
        path_config_file = os.path.join(path_config, file)
        file_settings = NewtFiles.read_json_from_file(path_config_file)
        NewtCons.validate_input(
            file_settings, dict, check_non_empty=True,
            location="mwparser.check_todo : file_settings"
        )
        assert isinstance(file_settings, dict)  # for type checker

        # Check required keys in file_settings
        required_keys = {"FOLDER_LINK", "BASE_URL"}
        NewtUtil.check_dict_keys(file_settings, required_keys)
        for value in file_settings.values():
            NewtCons.validate_input(
                value, str, check_non_empty=True,
                location="mwparser.check_todo : file_settings[value]"
            )

        # Check if namespace_types.json exists for the config
        path_namespace_types = os.path.join(DIR_GLOBAL, file_settings["FOLDER_LINK"], FILE_NAMESPACES)
        if not os.path.isfile(path_namespace_types):
            NewtCons.error_msg(
                f"Missing namespace_types.json for config: {file}",
                f"File must be here: {path_namespace_types}",
                location="mwparser.check_todo : namespace_types.json missing"
            )

        # Get namespace types from file
        ns_dict = NewtFiles.read_json_from_file(path_namespace_types)
        NewtCons.validate_input(
            ns_dict, dict, check_non_empty=True,
            location="mwparser.check_todo : ns_dict"
        )
        assert isinstance(ns_dict, dict)

        # Calculate max key length from namespace types for formatting
        max_key_len = len(max(ns_dict.keys(), key=len))

        path_logs = os.path.join(DIR_GLOBAL, file_settings["FOLDER_LINK"], FOLDER_LOGS)

        for wiki_data_type in WIKI_DATA_TYPE_DICT.values():
            if wiki_data_type in ("allpages", "pageids"):
                for ns_key, ns_value in ns_dict.items():
                    name_wiki_log_file = f"{wiki_data_type}-{int(ns_key):0{max_key_len}d}.txt"
                    path_wiki_log_file = os.path.join(path_logs, name_wiki_log_file)
                    if not os.path.isfile(path_wiki_log_file):
                        todo_list.append((file, wiki_data_type, ns_key, ns_value))
            else:
                name_wiki_log_file = f"{wiki_data_type}.txt"
                path_wiki_log_file = os.path.join(path_logs, name_wiki_log_file)
                if not os.path.isfile(path_wiki_log_file):
                    todo_list.append((file, wiki_data_type, None, None))

    print()
    print("=== TODO LIST ===")
    todo_list.reverse()
    for todo in todo_list:
        print(todo)
    print()

    return todo_list


def read_config(
        ) -> dict:
    """Read configuration from a selected JSON file."""

    global file_config_set
    global wiki_data_type_set
    global namespace_types_set
    global namespace_nr_set

    # Select WIKI Project
    # Settings are at file beginning of script
    if FOLDER_CONFIG_CHECK:
        count_file_config = NewtUtil.count_similar_values(TODO_LIST, 0)
        file_config_set = NewtFiles.choose_file_from_folder(
            os.path.join(DIR_PROJECT, "configs"),
            count_file_config
        )

    # Be sure return value or global variable is set to a non-empty str
    NewtCons.validate_input(
        file_config_set, str, check_non_empty=True,
        location="mwparser.read_config : file_config_set"
    )
    assert isinstance(file_config_set, str)  # for type checker

    # Get settings content from config file
    # Its structure is already checked in check_todo() function, so we can be sure it has all required keys and values
    path_config_file = os.path.join(DIR_PROJECT, "configs", file_config_set)
    settings = NewtFiles.read_json_from_file(path_config_file)
    NewtCons.validate_input(
        settings, dict, check_non_empty=True,
        location="mwparser.read_config : settings"
    )
    assert isinstance(settings, dict)  # for type checker

    # Select WIKI Data Type
    if WIKI_DATA_TYPE_CHECK:
        print()
        count_wiki_data_types = NewtUtil.count_similar_values(
            [todo for todo in TODO_LIST if todo[0] == file_config_set], 1
        )
        wiki_data_type_nr = NewtUtil.select_from_input(WIKI_DATA_TYPE_DICT, count_wiki_data_types)
        wiki_data_type_set = WIKI_DATA_TYPE_DICT[wiki_data_type_nr]

    # Be sure return value or global variable is set to a non-empty str
    NewtCons.validate_input(
        wiki_data_type_set, str, check_non_empty=True,
        location="mwparser.read_config : wiki_data_type_set"
    )
    assert isinstance(wiki_data_type_set, str)  # for type checker

    namespace_types_set = NewtFiles.read_json_from_file(
        os.path.join(DIR_GLOBAL, settings["FOLDER_LINK"], FILE_NAMESPACES)
    )

    # Be sure return value or global variable is set to a non-empty dict
    NewtCons.validate_input(
        namespace_types_set, dict, check_non_empty=True,
        location="mwparser.read_config : namespace_types_set"
    )
    assert isinstance(namespace_types_set, dict)  # for type checker

    # Calculate max key length from namespace types for formatting
    settings["ns_max_key_len"] = len(max(namespace_types_set.keys(), key=len))

    # Select Namespace Number if needed (for types with multiple namespaces)
    if wiki_data_type_set in (
        "allpages",
        "pageids",
    ):
        if NAMESPACE_NR_CHECK:
            print()
            count_namespace_types = NewtUtil.count_similar_values(
                [todo for todo in TODO_LIST if todo[0] == file_config_set and todo[1] == wiki_data_type_set], 3
            )
            namespace_nr_set = NewtUtil.select_from_input(namespace_types_set, count_namespace_types)
            namespace_nr_set = int(namespace_nr_set)

    match wiki_data_type_set:
        case "allpages":
            settings["file_name"] = os.path.join("allpages", f"{namespace_nr_set:0{settings["ns_max_key_len"]}d}.csv")

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

        case _:
            NewtCons.error_msg(
                f"Unexpected wiki_data_type_set: {wiki_data_type_set}",
                location="mwparser.read_config : match wiki_data_type_set default case"
            )

    return settings


def prep_headers_params_for_url(
        ) -> tuple:
    """Set headers and parameters for the URL request based on settings."""

    global namespace_nr_set
    global time_end
    global time_start
    global wiki_data_type_set

    headers = {
        "User-Agent": "MyGuildWarsBot/1.2 (burova.anna+parser+bot@gmail.com)",
        "Accept-Encoding": "gzip",
    }

    params = {
        "action": "query",
        "format": "json",
        "maxlag": "2",
        "utf8": "true",
        "formatversion": "2",
    }

    match wiki_data_type_set:
        case "allpages":
            params.update({"list": "allpages"})
            params.update({"aplimit": "max"})
            params.update({"apnamespace": str(namespace_nr_set)})

        case "pageids":
            params.update({"prop": "revisions"})
            params.update({"rvprop": "content"})
            params.update({"rvslots": "*"})

        case "recentchanges":
            params.update({"list": "recentchanges"})
            params.update({"rcnamespace": "*"})
            params.update({"rclimit": "max"})
            params.update({"rcstart": str(time_start)})
            params.update({"rcend": str(time_end)})

        case "pagesrecent":
            params.update({"prop": "revisions"})
            params.update({"rvprop": "content"})
            params.update({"rvslots": "*"})

        case "savefiles":
            params.update({"maxlag": "5"})
            params.update({"prop": "imageinfo"})
            params.update({"iiprop": "url"})

        case _:
            pass

    if wiki_data_type_set == "allpages":
        if APCONTINUE_CHECK:
            params.update({"apcontinue": APCONTINUE_PARAM})

    return (headers, params)


def get_blocked_set(
        ) -> set[str]:
    """Read blocked list from file and return as a set."""

    blocked_set = set()
    path_file_blocked = os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FOLDER_LISTS, FILE_BLOCKED)
    blocked_list = NewtFiles.read_text_from_file(path_file_blocked)
    print()

    if blocked_list:
        for line in blocked_list.splitlines():
            line = line.strip()
            if line:
                blocked_set.add(line)

    return blocked_set


def get_json_from_url(
        continue_page_wiki: str | None = None,
        continue_page_backup: str | None = None
        ) -> dict:
    """Fetch JSON data from a URL based on settings and save to file."""

    global wiki_data_type_set

    headers, params = headers_params_for_url

    match wiki_data_type_set:
        case "allpages":
            if continue_page_wiki is not None:
                if continue_page_wiki in BLOCKED_SET and continue_page_backup is not None:
                    print(continue_page_wiki)
                    continue_page_wiki = continue_page_backup

                print(continue_page_wiki)
                params.update({"apcontinue": continue_page_wiki})


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

        case _:
            pass

    data_from_url = NewtNet.fetch_data_from_url(
        SETTINGS["BASE_URL"], params, headers,
        mode="auto", repeat_on_fail=False
    )
    print()

    # None data mostly comes from 403 Forbidden error, so we save continue_page_wiki to blocked list and skip it next time
    if data_from_url is None:
        if continue_page_wiki is not None:
            path_file_blocked = os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FOLDER_LISTS, FILE_BLOCKED)
            NewtFiles.save_text_to_file(
                path_file_blocked,
                continue_page_wiki,
                append=True
            )

        NewtCons.error_msg(
            "Failed to read config JSON, exiting",
            location="mwparser.get_json_from_url : data_from_url=None"
        )
    # ensure the type checker knows choose_config is not None
    assert data_from_url is not None

    if len(data_from_url) > 500000:
        # Need to try to split request into pieces, to be sure it will return all data
        data_from_url_chunks = {'batchcomplete': True, 'query': {'pages': []}}

        if settings["config_type"] == "pageids":
            for index_range in range(index_start, index_end):
                params.update({"pageids": str(settings["allpages_ids"][index_range])})

                data_from_url_small = NewtNet.fetch_data_from_url(
                    settings["BASE_URL"], params, headers,
                    mode="manual", repeat_on_fail=True
                )
                print()

                # ensure the type checker knows settings is not None and is a dict
                if data_from_url_small is None:
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
                assert data_from_url_small is not None
                json_from_url_small = NewtFiles.convert_str_to_json(data_from_url_small)
                NewtCons.validate_input(
                    json_from_url_small, dict,
                    location="mwparser.get_json_from_url : json_from_url_small != dict"
                )
                assert isinstance(json_from_url_small, dict)
                data_from_url_chunks['query']['pages'].extend(
                    json_from_url_small.get('query', {}).get('pages', [])
                )

        else:
            NewtCons.error_msg(
                "Data from URL is too large, but cannot split further.",
                location="mwparser.get_json_from_url : len(data_from_url) > 500000"
            )

        json_from_url = data_from_url_chunks

    else:
        json_from_url = NewtFiles.convert_str_to_json(data_from_url)

    # Ensure return value is a dict
    NewtCons.validate_input(
        data_from_url, str, check_non_empty=True,
        location="mwparser.get_json_from_url : data_from_url"
    )
    assert isinstance(data_from_url, str)  # for type checker
    json_from_url = NewtFiles.convert_str_to_json(data_from_url)

    NewtCons.validate_input(
        json_from_url, dict, check_non_empty=True,
        location="mwparser.get_json_from_url : json_from_url"
    )
    assert isinstance(json_from_url, dict)  # for type checker

    return json_from_url


def restructure_json_allpages(
        json_data_dict: dict
        ) -> tuple[list[str], str]:
    """Process and save all pages from JSON data."""

    if "continue" in json_data_dict:
        required_keys_json = {"query", "continue", "batchcomplete", "limits"}
        NewtUtil.check_dict_keys(json_data_dict, required_keys_json)
    else:
        required_keys_json = {"query", "batchcomplete", "limits"}
        NewtUtil.check_dict_keys(json_data_dict, required_keys_json)

    required_keys_query = {"allpages"}
    NewtUtil.check_dict_keys(json_data_dict["query"], required_keys_query)

    allpages_list = []
    allpages_list.append(["pageid", "title"])
    mw_apcontinue = ""
    for page in json_data_dict["query"]["allpages"]:
        required_keys_allpages = {"pageid", "ns", "title"}
        NewtUtil.check_dict_keys(page, required_keys_allpages)

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
        NewtUtil.check_dict_keys(json_data_dict, required_keys_json)
    else:
        required_keys_json = {"query", "batchcomplete", "limits"}
        NewtUtil.check_dict_keys(json_data_dict, required_keys_json)

    required_keys_query = {"recentchanges"}
    NewtUtil.check_dict_keys(json_data_dict["query"], required_keys_query)

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
        NewtUtil.check_dict_keys(page, required_keys_recentchanges, stop=False)

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
    NewtUtil.check_dict_keys(json_data_dict, required_keys_json)
    required_keys_query = {"pages"}
    NewtUtil.check_dict_keys(json_data_dict["query"], required_keys_query)

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
                        if NewtFiles.check_file_exists(missing_file):
                            NewtFiles.ensure_dir_exists(missing_target)
                            shutil.move(missing_file, missing_target)
                continue

        required_keys_page = {"pageid", "ns", "title", "revisions"}
        NewtUtil.check_dict_keys(page, required_keys_page, stop=False)

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
            NewtUtil.check_dict_keys(revision, required_keys_revision)
            required_keys_main = {"main"}
            NewtUtil.check_dict_keys(revision["slots"], required_keys_main)
            required_keys_content = {"contentmodel", "contentformat", "content"}
            NewtUtil.check_dict_keys(revision["slots"]["main"], required_keys_content)

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
    NewtUtil.check_dict_keys(json_data_dict, required_keys_json)
    required_keys_query = {"pages"}
    NewtUtil.check_dict_keys(json_data_dict["query"], required_keys_query)

    for image_info in json_data_dict["query"]["pages"]:
        if "imageinfo" not in image_info:
            continue

        required_keys_image = {"pageid", "ns", "title", "imagerepository", "imageinfo"}
        NewtUtil.check_dict_keys(image_info, required_keys_image, stop=False)

        if len(image_info["imageinfo"]) != 1:
            NewtCons.error_msg(
                f"Unexpected imageinfo length: {len(image_info['imageinfo'])} for image title: {image_info['title']}",
                location="mwparser.get_image_from_pages : len(image_info['imageinfo']) != 1"
            )
            continue

        required_keys_imageinfo = {"url", "descriptionurl", "descriptionshorturl"}
        NewtUtil.check_dict_keys(image_info["imageinfo"][0], required_keys_imageinfo, stop=False)

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


def save_data_list(
        data_list: list[str],
        append: bool = True
        ) -> None:
    """Save the restructured list data to a file."""

    if "file_name" not in SETTINGS:
        NewtCons.error_msg(
            "Missing 'file_name' in SETTINGS for saving data list",
            location="mwparser.save_data_list : file_name"
        )

    NewtFiles.save_csv_to_file(
        os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FOLDER_LISTS, SETTINGS["file_name"]),
        data_list,
        append=append
    )
    print()


def loop_next_pages(
        json_data: dict,
        continue_page_backup: str | None = None
        ) -> None:
    """Loop to fetch next pages based on the config type."""

    global wiki_data_type_set

    try:
        while True:
            match wiki_data_type_set:
                case "allpages":
                    if "continue" not in json_data:
                        break

                    required_keys_continue = {"apcontinue", "continue"}
                    NewtUtil.check_dict_keys(json_data["continue"], required_keys_continue)

                    json_data = get_json_from_url(
                        continue_page_wiki = json_data["continue"]["apcontinue"],
                        continue_page_backup = continue_page_backup
                        )

                    data_list, continue_page_backup = restructure_json_allpages(json_data)
                    save_data_list(data_list)

        elif settings["config_type"] == "recentchanges":
            while True:
                if "continue" not in json_data:
                    break

                required_keys = {"rccontinue", "continue"}
                NewtUtil.check_dict_keys(json_data["continue"], required_keys, stop=False)

                json_data = get_json_from_url(
                    continue_param = json_data["continue"]["rccontinue"]
                )

                list_data = restructure_json_recentchanges(json_data)

                save_list_data(list_data)

        elif settings["config_type"] in (
                "pageids",
                "pagesrecent",
                ):
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

                case _:
                    break

    except Exception as e:
        NewtCons.error_msg(
            f"Script encountered an error: {e}",
            location="mwparser.loop_next_pages : Exception"
        )

    except SystemExit:
        NewtCons.error_msg(
            "SystemExit on fetching all pages",
            location="mwparser.loop_next_pages : SystemExit"
        )


def remove_duplicated_lines(
        ) -> None:
    """Remove duplicated lines from the recentchanges file."""

    file_path = os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FOLDER_LISTS, SETTINGS["file_name"])
    lines = NewtFiles.read_csv_from_file(file_path)

    NewtCons.validate_input(
        lines, list, check_non_empty=True,
        location="mwparser.remove_duplicated_lines : lines"
    )
    assert isinstance(lines, list)  # for type checker

    # Separate header from data
    row_header = lines[0] if lines else []
    rows_data = lines[1:] if len(lines) > 1 else []

    # Ensure header does not exist in data_lines
    data_lines = [line for line in rows_data if line != row_header]

    # Remove duplicates from data only
    unique_lines = [list(t) for t in dict.fromkeys(map(tuple, data_lines))]
    unique_lines.sort()

    # Prepend header back
    sorted_lines = [row_header] + unique_lines

    NewtFiles.save_csv_to_file(
        file_path,
        sorted_lines
    )
    print()


if __name__ == "__main__":
    NewtCons.check_location(DIR_GLOBAL, MUST_LOCATION)
    TODO_LIST = check_todo()
    SETTINGS = read_config()
    headers_params_for_url = prep_headers_params_for_url()
    BLOCKED_SET = get_blocked_set()
    json_data = get_json_from_url()

    match wiki_data_type_set:
        case "allpages":
            data_list, continue_page_backup = restructure_json_allpages(json_data)
            save_data_list(data_list, False)
            loop_next_pages(json_data, continue_page_backup)
            remove_duplicated_lines()

        case "recentchanges":
            list_data = restructure_json_recentchanges(json_data)
            save_list_data(list_data, False)
            loop_next_pages(json_data)
            remove_duplicated_lines()

        case "pageids" | "pagesrecent" | "savefiles":
            loop_next_pages(json_data)

        case _:
            NewtCons.error_msg(
                f"Unexpected config type: {settings['config_type']}",
                location="mwparser.main : settings['config_type']"
            )

    print("=== END ===")

    if SAVE_LOG:
        if wiki_data_type_set in (
                "allpages",
                "pageids",
                ):
            file_target_name = f"{wiki_data_type_set}-{namespace_nr_set:0{SETTINGS["ns_max_key_len"]}d}.txt"
        else:
            file_target_name = f"{wiki_data_type_set}.txt"

        path_target = os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FOLDER_LOGS, file_target_name)

        NewtFiles.cleanup_logging(SETUP_LOGGING_DATA, path_target)
