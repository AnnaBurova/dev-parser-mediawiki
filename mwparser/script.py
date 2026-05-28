"""
Updated on 2026-05
Created on 2025-11

@author: NewtCode Anna Burova

> script.py xxx.json 1 6
"""

from __future__ import annotations

import sys
import os
import shutil
from datetime import datetime, timedelta, timezone

import newtutils.console as NewtCons
import newtutils.utility as NewtUtil
import newtutils.files as NewtFiles
# import newtutils.sql as NewtSQL
import newtutils.network as NewtNet

# ==============================================================================

DIR_PROJECT = os.path.dirname(os.path.realpath(__file__))
print("DIR_PROJECT:", DIR_PROJECT)
# D:\VS_Code\dev-parser-mediawiki\mwparser

DIR_GLOBAL = os.path.dirname(os.path.dirname(DIR_PROJECT))
print("DIR_GLOBAL: ", DIR_GLOBAL)
# D:\VS_Code

# Add the project root directory to sys.path
sys.path.append(DIR_GLOBAL)

MUST_LOCATION = os.path.join("D:\\", "VS_Code")  # TODO
print("MUST_LOCATION:", MUST_LOCATION)
# D:\VS_Code

# ==============================================================================

BACK_IN_TIME_DAYS = 7
TIME_NOW = datetime.now(timezone.utc)
time_start = TIME_NOW - timedelta(days=0, hours=0)
time_start = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")
time_end = TIME_NOW - timedelta(days=BACK_IN_TIME_DAYS, hours=0)
time_end = time_end.strftime("%Y-%m-%dT%H:%M:%SZ")

# ==============================================================================

FOLDER_PROJECT_CONFIGS = os.path.join(DIR_PROJECT, "configs")
FOLDER_RAW_PAGES = os.path.join("data", "raw", "pages")
FOLDER_RAW_REDIRECT = os.path.join("data", "raw", "redirect")
FOLDER_RAW_REMOVED = os.path.join("data", "raw", "removed")
FOLDER_RAW_IMAGES = os.path.join("data", "raw", "images")
FOLDER_LOGS = os.path.join("data", "logs")
FOLDER_LISTS = os.path.join("data", "lists")
FILE_BLOCKED = os.path.join(FOLDER_LISTS, "blocked.txt")
FILE_RECENTCHANGES = os.path.join(FOLDER_LISTS, "recentchanges.csv")
FILE_NAMESPACES = os.path.join("data", "schemas", "namespace_types.json")

# ==============================================================================

# g_file_config = NewtFiles.choose_file_from_folder() in read_config()
SELECT_CONFIG_FROM_FOLDER = True
# SELECT_CONFIG_FROM_FOLDER = False  # TODO
# If SELECT_CONFIG_FROM_FOLDER is False, set g_file_config here
g_file_config = "xxx.json"  # TODO
# dev-parser-mediawiki\mwparser\configs\xxx.json

if len(sys.argv) > 1 and sys.argv[1]:
    g_file_config = sys.argv[1]
    NewtFiles.check_file_exists(
        os.path.join(FOLDER_PROJECT_CONFIGS, g_file_config)
    )
    SELECT_CONFIG_FROM_FOLDER = False

# ==============================================================================

WIKI_LIST_TYPE_DICT = {
    "1": "allpages",
    "2": "pageids",
    "3": "recentchanges",
    "4": "pagesrecent",
    "5": "savefiles",
}

# g_wiki_list_type = NewtUtil.select_from_input() in read_config()
SELECT_WIKI_LIST_TYPE_FROM_INPUT = True
# SELECT_WIKI_LIST_TYPE_FROM_INPUT = False  # TODO
# If SELECT_WIKI_LIST_TYPE_FROM_INPUT is False, set g_wiki_list_type here
g_wiki_list_type = WIKI_LIST_TYPE_DICT["1"]  # TODO

if len(sys.argv) > 2 and sys.argv[2]:
    if sys.argv[2] in WIKI_LIST_TYPE_DICT:
        g_wiki_list_type = WIKI_LIST_TYPE_DICT[sys.argv[2]]
        SELECT_WIKI_LIST_TYPE_FROM_INPUT = False

# ==============================================================================

g_namespace_types_dict: dict = {}

# g_namespace_nr_int = NewtUtil.select_from_input() in read_config()
SELECT_NAMESPACE_NR_FROM_INPUT = True
# SELECT_NAMESPACE_NR_FROM_INPUT = False  # TODO
# If SELECT_NAMESPACE_NR_FROM_INPUT is False, set namespace_nr_int here
g_namespace_nr_int: int = 0  # TODO

if len(sys.argv) > 3 and sys.argv[3]:
    try:
        int(sys.argv[3])
    except ValueError as e:
        NewtCons.error_msg(
            f"ValueError: {e}",
            location="global.namespace_nr_int"
        )

    g_namespace_nr_int = int(sys.argv[3])
    SELECT_NAMESPACE_NR_FROM_INPUT = False

# ==============================================================================

# If APCONTINUE_PARAM is not empty, set apcontinue value here
# Extended functionality in prep_headers_params_for_url()
# params.update({"apcontinue": APCONTINUE_PARAM})
APCONTINUE_PARAM = ""  # TODO

# ==============================================================================

SETTING_INDEX_START = 0  # TODO
# in read_config()

# max 50 pages per MediaWiki Settings for no admin users
SETTING_INDEX_MAX_PAGES = 50  # TODO
# in get_json_from_url()

# max 25 titles per MediaWiki Settings for no admin users
SETTING_INDEX_MAX_TITLES = 25  # TODO
# in get_json_from_url()

# max 8 MB for images to avoid downloading very large files that may cause issues
SETTING_IMAGE_MAX_MB_SIZE = 8  # TODO
# in restructure_json_savefiles()

# ==============================================================================

PRINT_LOG = True
# PRINT_LOG = False  # TODO

SAVE_LOG = True
# SAVE_LOG = False  # TODO

FETCH_MODE = "auto"
# FETCH_MODE = "alert"
# FETCH_MODE = "manual"

# ==============================================================================


def fetch_data_from_mediawiki(
        base_url: str,
        additional_params: dict[str, str]
        ) -> str | bool:

    headers: dict[str, str] = {
        "User-Agent": "MyGuildWarsBot/1.3 (burova.anna+mwparser@gmail.com)",
        "Accept-Encoding": "gzip",
    }

    params: dict[str, str] = {
        "action": "query",
        "format": "json",
        "maxlag": "5",
        "utf8": "true",
        "formatversion": "2",
    }

    params.update(additional_params)

    data_from_url = NewtNet.fetch_data_from_url(
        base_url, headers, params,
        mode=FETCH_MODE, print_log=PRINT_LOG
    )

    return data_from_url


def create_namespace_types_file(
        base_url: str,
        file_namespace_types: str
        ):

    namespace_types_params: dict[str, str] = {
        "meta": "siteinfo",
        "siprop": "namespaces",
    }

    data_str = fetch_data_from_mediawiki(base_url, namespace_types_params)
    NewtCons.validate_type(
        data_str, str, check_non_empty=True,
        location="mwparser.create_namespace_types_file : data_str"
    )
    assert isinstance(data_str, str)

    data_dict = NewtFiles.convert_str_to_json(data_str)
    NewtCons.validate_type(
        data_dict, dict, check_non_empty=True,
        location="mwparser.create_namespace_types_file : data_dict"
    )
    assert isinstance(data_dict, dict)

    NewtUtil.check_dict_keys(
        data_dict, {"batchcomplete", "query"},
        location="mwparser.create_namespace_types_file : data_dict"
    )

    NewtUtil.check_dict_keys(
        data_dict["query"], {"namespaces"},
        location="mwparser.create_namespace_types_file : data_dict[query]"
    )

    namespaces = {}
    for ns_nr, ns_data in data_dict["query"]["namespaces"].items():

        if ns_data["name"] == "":
            ns_data["name"] = "Main"
        if ns_data["name"] == "Talk":
            ns_data["name"] = "Main Talk"

        if all(key in ns_data for key in [
            "canonical", "namespaceprotection", "defaultcontentmodel"
        ]):
            NewtUtil.check_dict_keys(
                ns_data, {"id", "case", "name", "subpages", "content", "nonincludable",
                          "canonical", "namespaceprotection", "defaultcontentmodel"},
                location="mwparser.create_namespace_types_file : data_dict[query][namespaces]"
                    + " + namespaceprotection + defaultcontentmodel"
            )

        elif all(key in ns_data for key in ["canonical", "namespaceprotection"]):
            NewtUtil.check_dict_keys(
                ns_data, {"id", "case", "name", "subpages", "content", "nonincludable",
                          "canonical", "namespaceprotection"},
                location="mwparser.create_namespace_types_file : data_dict[query][namespaces]"
                    + " + namespaceprotection"
            )

        elif all(key in ns_data for key in ["canonical", "defaultcontentmodel"]):
            NewtUtil.check_dict_keys(
                ns_data, {"id", "case", "name", "subpages", "content", "nonincludable",
                          "canonical", "defaultcontentmodel"},
                location="mwparser.create_namespace_types_file : data_dict[query][namespaces]"
                    + " + defaultcontentmodel"
            )

        elif "canonical" in ns_data:
            NewtUtil.check_dict_keys(
                ns_data, {"id", "case", "name", "subpages", "content", "nonincludable",
                          "canonical"},
                location="mwparser.create_namespace_types_file : data_dict[query][namespaces]"
                    + " + canonical"
            )

        else:
            NewtUtil.check_dict_keys(
                ns_data, {"id", "case", "name", "subpages", "content", "nonincludable"},
                location="mwparser.create_namespace_types_file : data_dict[query][namespaces]"
                    + " + else"
            )
            namespaces[str(ns_nr)] = ns_data["name"]
            continue

        if ns_data["canonical"] == "":
            ns_data["canonical"] = "Main"
        if ns_data["canonical"] == "Talk":
            ns_data["canonical"] = "Main Talk"

        if ns_data["name"] == ns_data["canonical"]:
            namespaces[str(ns_nr)] = ns_data["name"]
        else:
            namespaces[str(ns_nr)] = f"{ns_data["name"]} ({ns_data["canonical"]})"

    NewtFiles.save_json_to_file(file_namespace_types, namespaces)


def check_todo(
        ) -> list[tuple[str, str, str]]:
    """ Check for missing log files based on existing config files and return a list of tasks to do. """

    todo_list: list[tuple] = []

    for p_file in os.listdir(FOLDER_PROJECT_CONFIGS):
        file_project_config = os.path.join(FOLDER_PROJECT_CONFIGS, p_file)

        # Skip if it's not a file (e.g., directory)
        if not os.path.isfile(file_project_config):
            continue

        # Skip non-config files
        if not p_file.endswith(".json"):
            NewtCons.error_msg(
                f"Found non-config file: {p_file}",
                location="mwparser.check_todo : not p_file.endswith(.json)",
                stop=False
            )
            continue

        # Skip specific config example file
        if p_file == "xxx.json":
            continue

        # Get settings from config file
        json_file_settings = NewtFiles.read_json_from_file(file_project_config)
        NewtCons.validate_type(
            json_file_settings, dict, check_non_empty=True,
            location="mwparser.check_todo : json_file_settings"
        )
        assert isinstance(json_file_settings, dict)  # for type checker

        # Check required keys in json_file_settings
        NewtUtil.check_dict_keys(
            json_file_settings, {"FOLDER_LINK", "BASE_URL"},
            location="mwparser.check_todo : json_file_settings"
        )

        for value in json_file_settings.values():
            NewtCons.validate_type(
                value, str, check_non_empty=True,
                location="mwparser.check_todo : json_file_settings[value]"
            )

        # Check if namespace_types.json exists for the config
        file_namespace_types = os.path.join(
            DIR_GLOBAL, json_file_settings["FOLDER_LINK"], FILE_NAMESPACES)

        if not NewtFiles.check_file_exists(file_namespace_types, stop=False):
            create_namespace_types_file(json_file_settings["BASE_URL"], file_namespace_types)

        if not os.path.isfile(file_namespace_types):
            NewtCons.error_msg(
                f"Missing namespace_types.json for config: {p_file}",
                f"File must be here: {file_namespace_types}",
                location="mwparser.check_todo : namespace_types.json missing"
            )

        # Get namespace types from file
        namespace_dict = NewtFiles.read_json_from_file(file_namespace_types)
        NewtCons.validate_type(
            namespace_dict, dict, check_non_empty=True,
            location="mwparser.check_todo : namespace_dict"
        )
        assert isinstance(namespace_dict, dict)

        # Calculate max key length from namespace types for formatting
        ns_dict_key_len = len(max(namespace_dict.keys(), key=len))

        # Check folder with logs to find missing logs for todo
        folder_with_logs = os.path.join(
            DIR_GLOBAL, json_file_settings["FOLDER_LINK"], FOLDER_LOGS)

        # Check if each wiki list type has log file
        for wiki_list_type in WIKI_LIST_TYPE_DICT.values():

            # This types has sub log for each namespace
            if wiki_list_type in ("allpages", "pageids"):
                for ns_key, ns_value in namespace_dict.items():
                    file_wiki_log = f"{wiki_list_type}-{int(ns_key):0{ns_dict_key_len}d}.txt"
                    path_wiki_log = os.path.join(folder_with_logs, file_wiki_log)
                    if not os.path.isfile(path_wiki_log):
                        todo_list.append((p_file, wiki_list_type, ns_key, ns_value))

            # Other types dont have sub logs, only 1
            else:
                file_wiki_log = f"{wiki_list_type}.txt"
                path_wiki_log = os.path.join(folder_with_logs, file_wiki_log)
                if not os.path.isfile(path_wiki_log):
                    todo_list.append((p_file, wiki_list_type, None, None))

    if todo_list and PRINT_LOG:
        print()
        print("=== TODO LIST ===")
        todo_list.reverse()
        for todo in todo_list:
            print(todo)

    return todo_list


def read_config(
        ) -> dict:
    """Read configuration from a selected JSON file."""

    global g_file_config
    global g_wiki_list_type
    global g_namespace_types_dict
    global g_namespace_nr_int

    # Select WIKI Project
    # Settings are at file beginning of script
    if SELECT_CONFIG_FROM_FOLDER:
        count_file_config = NewtUtil.count_values_by_position(TODO_LIST, 0)
        g_file_config = NewtFiles.choose_file_from_folder(
            FOLDER_PROJECT_CONFIGS,
            count_file_config
        )

    # Be sure return value or global variable is set to a non-empty str
    NewtCons.validate_type(
        g_file_config, str, check_non_empty=True,
        location="mwparser.read_config : g_file_config"
    )
    assert isinstance(g_file_config, str)  # for type checker

    # Get settings content from config file
    # Its structure is already checked in check_todo() function, so we can be sure it has all required keys and values
    path_config_file = os.path.join(FOLDER_PROJECT_CONFIGS, g_file_config)
    settings = NewtFiles.read_json_from_file(path_config_file)
    NewtCons.validate_type(
        settings, dict, check_non_empty=True,
        location="mwparser.read_config : settings"
    )
    assert isinstance(settings, dict)  # for type checker

    # Select WIKI Data Type
    if SELECT_WIKI_LIST_TYPE_FROM_INPUT:
        print()
        count_wiki_data_types = NewtUtil.count_values_by_position(
            [todo for todo in TODO_LIST if todo[0] == g_file_config], 1
        )
        wiki_data_type_nr = NewtUtil.select_from_input(WIKI_LIST_TYPE_DICT, count_wiki_data_types)
        g_wiki_list_type = WIKI_LIST_TYPE_DICT[wiki_data_type_nr]

    # Be sure return value or global variable is set to a non-empty str
    NewtCons.validate_type(
        g_wiki_list_type, str, check_non_empty=True,
        location="mwparser.read_config : g_wiki_list_type"
    )
    assert isinstance(g_wiki_list_type, str)  # for type checker

    namespace_types_data = NewtFiles.read_json_from_file(
        os.path.join(DIR_GLOBAL, settings["FOLDER_LINK"], FILE_NAMESPACES)
    )
    # Be sure return value or global variable is set to a non-empty dict
    NewtCons.validate_type(
        namespace_types_data, dict, check_non_empty=True,
        location="mwparser.read_config : namespace_types_data"
    )
    assert isinstance(namespace_types_data, dict)  # for type checker
    g_namespace_types_dict = namespace_types_data

    # Calculate max key length from namespace types for formatting
    settings["ns_max_key_len"] = len(max(g_namespace_types_dict.keys(), key=len))

    # Select Namespace Number if needed (for types with multiple namespaces)
    if g_wiki_list_type in (
        "allpages",
        "pageids",
    ):
        if SELECT_NAMESPACE_NR_FROM_INPUT:
            print()
            count_namespace_types = NewtUtil.count_values_by_position(
                [todo for todo in TODO_LIST if todo[0] == g_file_config and todo[1] == g_wiki_list_type], 3
            )
            namespace_nr_set_str = NewtUtil.select_from_input(g_namespace_types_dict, count_namespace_types)
            g_namespace_nr_int = int(namespace_nr_set_str)

    elif g_wiki_list_type == "savefiles":
        namespace_file = "File"
        keys = [key for key, val in g_namespace_types_dict.items() if val == namespace_file]

        if len(keys) != 1:
            NewtCons.error_msg(
                f"Unexpected result of namespaces with value '{namespace_file}':",
                f"Keys: {keys}",
                location="mwparser.read_config : savefiles"
            )
        g_namespace_nr_int = int(keys[0])

    match g_wiki_list_type:
        case "allpages":
            settings["file_name"] = os.path.join("allpages", f"{g_namespace_nr_int:0{settings['ns_max_key_len']}d}.csv")

        case "pageids":
            for folder_type in (FOLDER_RAW_PAGES, FOLDER_RAW_REDIRECT, FOLDER_RAW_REMOVED):
                folder_to_remove = os.path.join(
                    DIR_GLOBAL, settings["FOLDER_LINK"], folder_type,
                    str(g_namespace_nr_int).zfill(settings["ns_max_key_len"])
                )
                if os.path.isdir(folder_to_remove):
                    print(f"Removing folder: {folder_to_remove}")
                    shutil.rmtree(folder_to_remove)

            settings["index_start"] = SETTING_INDEX_START
            path_allpages = os.path.join(
                DIR_GLOBAL, settings["FOLDER_LINK"], FOLDER_LISTS,
                "allpages", f"{g_namespace_nr_int:0{settings['ns_max_key_len']}d}.csv"
            )
            list_allpages = NewtFiles.read_csv_from_file(path_allpages)

            NewtCons.validate_type(
                list_allpages, list, check_non_empty=True,
                location="mwparser.read_config : list_allpages"
            )
            assert isinstance(list_allpages, list)  # for type checker

            # skip header and get only ids from first column
            settings["page_ids"] = sorted([int(row[0]) for row in list_allpages[1:]])

        case "recentchanges":
            settings["file_name"] = FILE_RECENTCHANGES

        case "pagesrecent":
            settings["index_start"] = SETTING_INDEX_START
            path_recentchanges = os.path.join(DIR_GLOBAL, settings["FOLDER_LINK"], FILE_RECENTCHANGES)
            list_recentchanges = NewtFiles.read_csv_from_file(path_recentchanges)

            NewtCons.validate_type(
                list_recentchanges, list, check_non_empty=True,
                location="mwparser.read_config : list_recentchanges"
            )
            assert isinstance(list_recentchanges, list)  # for type checker

            # skip header and get only ids from second column, convert them to int, filter out 0, check unique and sort
            settings["page_ids"] = sorted(list(set([int(row[1]) for row in list_recentchanges[1:] if int(row[1]) > 0])))

        case "savefiles":
            settings["index_start"] = SETTING_INDEX_START
            path_allpages = os.path.join(
                DIR_GLOBAL, settings["FOLDER_LINK"], FOLDER_LISTS,
                "allpages", f"{g_namespace_nr_int:0{settings['ns_max_key_len']}d}.csv"
            )
            list_files = NewtFiles.read_csv_from_file(path_allpages)

            NewtCons.validate_type(
                list_files, list, check_non_empty=True,
                location="mwparser.read_config : list_files"
            )
            assert isinstance(list_files, list)  # for type checker

            # skip header
            settings["files_titles"] = sorted([str(row[1]) for row in list_files[1:]])

        case _:
            NewtCons.error_msg(
                f"Unexpected g_wiki_list_type: {g_wiki_list_type}",
                location="mwparser.read_config : match g_wiki_list_type default case"
            )

    return settings


def prep_headers_params_for_url(
        ) -> tuple:
    """Set headers and parameters for the URL request based on settings."""

    global time_start
    global time_end
    global g_wiki_list_type
    global g_namespace_nr_int

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

    match g_wiki_list_type:
        case "allpages":
            params.update({"list": "allpages"})
            params.update({"aplimit": "max"})
            params.update({"apnamespace": str(g_namespace_nr_int)})

        case "pageids" | "pagesrecent":
            params.update({"prop": "revisions"})
            params.update({"rvprop": "content"})
            params.update({"rvslots": "*"})

        case "recentchanges":
            params.update({"list": "recentchanges"})
            params.update({"rcnamespace": "*"})
            params.update({"rclimit": "max"})
            params.update({"rcstart": str(time_start)})
            params.update({"rcend": str(time_end)})

        case "savefiles":
            params.update({"maxlag": "5"})
            params.update({"prop": "imageinfo"})
            params.update({"iiprop": "url"})

        case _:
            NewtCons.error_msg(
                f"Unexpected config type: {g_wiki_list_type}",
                location="mwparser.prep_headers_params_for_url : g_wiki_list_type default case"
            )

    if g_wiki_list_type == "allpages":
        if APCONTINUE_PARAM:
            params.update({"apcontinue": APCONTINUE_PARAM})

    return (headers, params)


def get_blocked_set(
        ) -> set[str]:
    """Read blocked list from file and return as a set."""

    blocked_set = set()
    path_file_blocked = os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FILE_BLOCKED)
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

    global g_wiki_list_type
    global g_namespace_types_dict

    path_file_blocked = os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FILE_BLOCKED)
    continue_page_for_block = None

    headers, params = headers_params_for_url

    match g_wiki_list_type:
        case "allpages":
            if continue_page_wiki is not None:
                # continue_page_wiki - current page title from wiki
                # continue_page_backup - previous page title from wiki, we saved in case current page is blocked
                # continue_page_for_block - what we will block incase no result
                continue_page_wiki = continue_page_wiki.replace(" ", "_")
                continue_page_for_block = continue_page_wiki
                if continue_page_wiki in BLOCKED_SET and continue_page_backup is not None:
                    print(continue_page_wiki)
                    continue_page_wiki = continue_page_backup.replace(" ", "_")
                    continue_page_for_block = continue_page_wiki

                print(continue_page_wiki)
                # Only without left and sep parts it will work in continue
                left_part, sep_part, right_part = continue_page_wiki.partition(":")
                if sep_part and left_part in set(g_namespace_types_dict.values()):
                    continue_page_wiki = right_part

                params.update({"apcontinue": continue_page_wiki})

        case "pageids" | "pagesrecent":
            if len(SETTINGS["page_ids"]) == 0:
                print()
                print("No pages to process. Empty list.")
                return {}

            index_start = SETTINGS["index_start"]
            index_max = SETTING_INDEX_MAX_PAGES
            index_end = index_start + index_max

            if len(SETTINGS["page_ids"]) < index_start:
                print()
                print("No more pages to process.")
                return {}

            params.update({"pageids": "|".join(
                map(str, SETTINGS["page_ids"][index_start:index_end])
            )})
            SETTINGS["index_start"] = index_end

            print()
            print(f"Processing page IDs from index {index_start} to {index_end}")
            print(f"Progress max index: {len(SETTINGS['page_ids'])}")
            print(f"Processing current page: {index_start / index_max}")
            print(f"Progress max pages: {len(SETTINGS['page_ids']) / index_max}")
            print()

        case "recentchanges":
            if continue_page_wiki is not None:
                print(continue_page_wiki)
                params.update({"rccontinue": continue_page_wiki})

        case "savefiles":
            if len(SETTINGS["files_titles"]) == 0:
                print()
                print("No images to process. Empty list.")
                return {}

            index_start = SETTINGS["index_start"]
            index_max = SETTING_INDEX_MAX_TITLES
            index_end = index_start + index_max

            if len(SETTINGS["files_titles"]) < index_start:
                print()
                print("No more images to process.")
                return {}

            params.update({"titles": "|".join(
                map(str, SETTINGS["files_titles"][index_start:index_end])
            )})
            SETTINGS["index_start"] = index_end

            print()
            print(f"Processing images IDs from index {index_start} to {index_end}")
            print(f"Progress max index: {len(SETTINGS['files_titles'])}")
            print(f"Processing current images: {index_start / index_max}")
            print(f"Progress max pages: {len(SETTINGS['files_titles']) / index_max}")
            print()

        case _:
            NewtCons.error_msg(
                f"Unexpected config type: {g_wiki_list_type}",
                location="mwparser.get_json_from_url : g_wiki_list_type default case"
            )

    data_from_url = NewtNet.fetch_data_from_url(
        SETTINGS["BASE_URL"], params, headers,
        mode="auto", print_log=PRINT_LOG
    )
    print()

    # None data mostly comes from 403 Forbidden error, so we save continue_page_for_block to blocked list and skip it next time
    if not data_from_url:
        if continue_page_for_block is not None:
            NewtFiles.save_text_to_file(
                path_file_blocked,
                continue_page_for_block,
                append=True
            )

        NewtCons.error_msg(
            "Failed to read JSON result, exiting",
            location="mwparser.get_json_from_url : data_from_url=False"
        )

    # Ensure return value is a dict
    NewtCons.validate_type(
        data_from_url, str, check_non_empty=True,
        location="mwparser.get_json_from_url : data_from_url"
    )
    assert isinstance(data_from_url, str)  # for type checker

    json_from_url = NewtFiles.convert_str_to_json(data_from_url)

    if json_from_url is None:
        # If text is too long, it may be incomplete,
        # so we need to try to split request into pieces, if possible, to be sure it will return all data
        data_from_url_chunks = {"batchcomplete": True, "query": {"pages": []}}

        if g_wiki_list_type in (
                "pageids",
                "pagesrecent",
                ):
            for index_range in range(index_start, index_end):
                if len(SETTINGS["page_ids"]) <= index_range:
                    break

                params.update({"pageids": str(SETTINGS["page_ids"][index_range])})

                data_from_url_small = NewtNet.fetch_data_from_url(
                    SETTINGS["BASE_URL"], params, headers,
                    mode="auto", print_log=PRINT_LOG
                )
                print()

                # None data mostly comes from 403 Forbidden error, so we need to catch page id and add it to blocked list to skip it next time
                if not data_from_url_small:
                    NewtFiles.save_text_to_file(
                        path_file_blocked,
                        f"---> Page ID: {SETTINGS['page_ids'][index_range]}",
                        append=True
                    )
                    NewtCons.error_msg(
                        "Failed to read small JSON result, exiting",
                        f"Page ID: {SETTINGS['page_ids'][index_range]}",
                        location="mwparser.get_json_from_url : data_from_url_small=False"
                    )

                # Ensure return value is a dict
                NewtCons.validate_type(
                    data_from_url_small, str, check_non_empty=True,
                    location="mwparser.get_json_from_url : data_from_url_small"
                )
                assert isinstance(data_from_url_small, str)  # for type checker

                json_from_url_small = NewtFiles.convert_str_to_json(data_from_url_small)

                if not NewtCons.validate_type(
                    json_from_url_small, dict, check_non_empty=True, stop=False,
                    location="mwparser.get_json_from_url : json_from_url_small != dict"
                ):
                    continue
                assert isinstance(json_from_url_small, dict)  # for type checker

                NewtUtil.check_dict_keys(
                    json_from_url_small, {"query", "batchcomplete"},
                    location="mwparser.get_json_from_url : json_from_url_small"
                )

                NewtUtil.check_dict_keys(
                    json_from_url_small["query"], {"pages"},
                    location="mwparser.get_json_from_url : json_from_url_small[query]"
                )

                data_from_url_chunks["query"]["pages"].extend(
                    json_from_url_small.get("query", {}).get("pages", [])
                )
        else:
            NewtCons.error_msg(
                "Failed to read JSON result, exiting",
                location="mwparser.get_json_from_url : json_from_url=False and not pageids"
            )

        json_from_url = data_from_url_chunks

    NewtCons.validate_type(
        json_from_url, dict, check_non_empty=True,
        location="mwparser.get_json_from_url : json_from_url"
    )
    assert isinstance(json_from_url, dict)  # for type checker

    return json_from_url


def restructure_json_allpages(
        json_data_dict: dict
        ) -> tuple[list[str], str]:
    """Process and save all pages from JSON data."""

    global g_namespace_nr_int

    if "continue" in json_data_dict:
        NewtUtil.check_dict_keys(
            json_data_dict, {"query", "batchcomplete", "limits", "continue"},
            location="mwparser.restructure_json_allpages : json_data_dict"
        )

    else:
        NewtUtil.check_dict_keys(
            json_data_dict, {"query", "batchcomplete", "limits"},
            location="mwparser.restructure_json_allpages : json_data_dict"
        )

    NewtUtil.check_dict_keys(
        json_data_dict["query"], {"allpages"},
        location="mwparser.restructure_json_allpages : json_data_dict[query]"
    )

    continue_page_backup = ""
    allpages_list = []
    allpages_list.append(["pageid", "title"])
    for page in json_data_dict["query"]["allpages"]:
        NewtUtil.check_dict_keys(
            page, {"pageid", "ns", "title"},
            location="mwparser.restructure_json_allpages : page"
        )

        if int(page["ns"]) != g_namespace_nr_int:
            NewtCons.error_msg(
                f"Unexpected namespace value: {page['ns']} for page ID {page['pageid']}",
                f"Page: {page}",
                location="mwparser.restructure_json_allpages : page[ns]"
            )

        if page["title"].replace(" ", "_") not in BLOCKED_SET:
            continue_page_backup = page["title"].replace(" ", "_")

        if page["title"].replace(" ", "_") in BLOCKED_SET:
            continue

        allpages_list.append([
            f"{page['pageid']:010d}",
            page["title"],
        ])

    return (allpages_list, continue_page_backup)


def restructure_json_pageids(
        json_data_dict: dict
        ) -> None:

    global g_wiki_list_type
    global g_namespace_types_dict
    global g_namespace_nr_int

    path_file_blocked = os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FILE_BLOCKED)
    path_recentchanges_missing = os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FILE_RECENTCHANGES)

    NewtUtil.check_dict_keys(
        json_data_dict, {"query", "batchcomplete"},
        location="mwparser.restructure_json_pageids : json_data_dict"
    )

    NewtUtil.check_dict_keys(
        json_data_dict["query"], {"pages"},
        location="mwparser.restructure_json_pageids : json_data_dict[query]"
    )

    for page in json_data_dict["query"]["pages"]:
        skip_page = False

        if "missing" in page:
            # Print warning to fix log later
            # Save this page id to recentchanges log to check later
            # Move affected files to removed folder to avoid processing them again until we check what is wrong with them
            NewtCons.error_msg(
                f"Page ID {page['pageid']} data is missing",
                f"Page: {page}",
                location="mwparser.restructure_json_pageids : 'missing' in page",
                stop=False
            )
            NewtFiles.save_text_to_file(
                path_recentchanges_missing, f"Page ID {page['pageid']} data is missing",
                append=True, print_log=False
            )
            for missing_folder in (FOLDER_RAW_PAGES, FOLDER_RAW_REDIRECT):
                for missing_namespace in g_namespace_types_dict.keys():
                    missing_file = os.path.join(
                        DIR_GLOBAL, SETTINGS["FOLDER_LINK"], missing_folder,
                        f"{int(missing_namespace):0{SETTINGS['ns_max_key_len']}d}", f"{page['pageid']:010d}.txt"
                    )
                    missing_target = os.path.join(
                        DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FOLDER_RAW_REMOVED,
                        f"{int(missing_namespace):0{SETTINGS['ns_max_key_len']}d}-{page['pageid']:010d}.txt"
                    )
                    if NewtFiles.check_file_exists(missing_file, stop=False, print_log=False):
                        NewtFiles.ensure_dir_exists(missing_target)
                        shutil.move(missing_file, missing_target)
                        NewtFiles.save_text_to_file(
                            path_recentchanges_missing, f"{missing_target}",
                            append=True, print_log=False
                        )
            continue

        NewtUtil.check_dict_keys(
            page, {"pageid", "ns", "title", "revisions"},
            location="mwparser.restructure_json_pageids : page"
        )

        check_ns = g_namespace_nr_int

        if g_wiki_list_type == "pagesrecent":
            if str(page["ns"]) in g_namespace_types_dict:
                check_ns = int(page["ns"])

        if int(page["ns"]) != check_ns:
            NewtCons.error_msg(
                f"Unexpected namespace value: {page['ns']} for page ID {page['pageid']}",
                f"Page: {page}",
                location="mwparser.restructure_json_pageids : page[ns]"
            )

        # Basic path for files to save
        folder_pages = FOLDER_RAW_PAGES

        text_for_file = ""
        text_for_file += f"Namespace ::: {page['ns']} ::: {g_namespace_types_dict[str(page['ns'])]}\n"
        text_for_file += f"Page ID   ::: {page['pageid']}\n"
        text_for_file += f"Title     ::: {page['title']}\n\n"

        for revision in page["revisions"]:
            NewtUtil.check_dict_keys(
                revision, {"slots"},
                location="mwparser.restructure_json_pageids : revision"
            )

            NewtUtil.check_dict_keys(
                revision["slots"], {"main"},
                location="mwparser.restructure_json_pageids : revision[slots]"
            )

            NewtUtil.check_dict_keys(
                revision["slots"]["main"], {"contentmodel", "contentformat", "content"},
                location="mwparser.restructure_json_pageids : revision[slots][main]"
            )

            if revision["slots"]["main"]["contentmodel"] != "wikitext":
                NewtCons.error_msg(
                    f"Unexpected Contentmodel : {revision['slots']['main']['contentmodel']}",
                    f"Title: {page['title']}",
                    f"Page: {page['pageid']}",
                    location="mwparser.restructure_json_pageids : revision[slots][main][contentmodel]",
                    stop=False
                )
                NewtFiles.save_text_to_file(
                    path_file_blocked,
                    page["title"].replace(" ", "_"),
                    append=True
                )
                skip_page = True
                break

            if revision["slots"]["main"]["contentformat"] != "text/x-wiki":
                NewtCons.error_msg(
                    f"Unexpected Contentformat : {revision['slots']['main']['contentformat']}",
                    f"Title: {page['title']}",
                    f"Page: {page['pageid']}",
                    location="mwparser.restructure_json_pageids : revision[slots][main][contentformat]"
                )

            if len(revision["slots"]["main"]["content"]) < 6:
                folder_pages = FOLDER_RAW_REMOVED

            if revision["slots"]["main"]["content"].lower().startswith("#redirect"):
                folder_pages = FOLDER_RAW_REDIRECT

            text_for_file += "-" * 80 + "\n"
            text_for_file += f"{revision['slots']['main']['content']}\n\n"

        # It helps to skip outer for if break was in inner for
        if skip_page:
            continue

        text_for_file += "=== END ==="

        path_file_pageid = os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], folder_pages, f"{g_namespace_nr_int:0{SETTINGS['ns_max_key_len']}d}", f"{page['pageid']:010d}.txt")
        NewtFiles.save_text_to_file(
            path_file_pageid,
            text_for_file,
            append=False
        )


def restructure_json_recentchanges(
        json_data_dict: dict
        ) -> list[str]:
    """Process and save all pages from JSON data."""

    global g_namespace_types_dict

    if "continue" in json_data_dict:
        NewtUtil.check_dict_keys(
            json_data_dict, {"query", "batchcomplete", "limits", "continue"},
            location="mwparser.restructure_json_recentchanges : json_data_dict"
        )

    else:
        NewtUtil.check_dict_keys(
            json_data_dict, {"query", "batchcomplete", "limits"},
            location="mwparser.restructure_json_recentchanges : json_data_dict"
        )

    NewtUtil.check_dict_keys(
        json_data_dict["query"], {"recentchanges"},
        location="mwparser.restructure_json_recentchanges : json_data_dict[query]"
    )

    recentchanges_list = []
    recentchanges_list.append(["timestamp", "pageid", "ns", "type", "title"])

    for page in json_data_dict["query"]["recentchanges"]:
        NewtUtil.check_dict_keys(
            page, {"type", "ns", "title", "pageid", "revid", "old_revid", "rcid", "timestamp"},
            location="mwparser.restructure_json_recentchanges : page"
        )

        if str(page["ns"]) not in g_namespace_types_dict:
            NewtCons.error_msg(
                f"Unexpected namespace value: {page['ns']} for page ID {page['title']}",
                f"Page: {page}",
                location="mwparser.restructure_json_recentchanges : page[ns]",
                stop=False
            )

        if page["pageid"] == 0:
            continue

        recentchanges_list.append([
            page["timestamp"],
            f"{page['pageid']:010d}",
            f"{page['ns']:0{SETTINGS['ns_max_key_len']}d}",
            f"{page['type']:>4}",
            page["title"],
        ])

    return recentchanges_list


def restructure_json_savefiles(
        json_data_dict: dict
        ) -> None:

    path_missing_image = os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FOLDER_LISTS, "missing-images.txt")

    if "batchcomplete" in json_data_dict:
        NewtUtil.check_dict_keys(
            json_data_dict, {"query", "batchcomplete"},
            location="mwparser.restructure_json_savefiles : json_data_dict + batchcomplete"
        )
    else:
        NewtUtil.check_dict_keys(
            json_data_dict, {"query", "continue"},
            location="mwparser.restructure_json_savefiles : json_data_dict + continue"
        )

    NewtUtil.check_dict_keys(
        json_data_dict["query"], {"pages"},
        location="mwparser.restructure_json_savefiles : json_data_dict[query]"
    )

    for image_data in json_data_dict["query"]["pages"]:
        if "imageinfo" in image_data:
            NewtUtil.check_dict_keys(
                image_data, {"pageid", "ns", "title", "imagerepository", "imageinfo"},
                location="mwparser.restructure_json_savefiles : image_data with imageinfo"
            )

        elif "pageid" in image_data:
            NewtUtil.check_dict_keys(
                image_data, {"pageid", "ns", "title", "imagerepository"},
                location="mwparser.restructure_json_savefiles : image_data without imageinfo"
            )

            NewtFiles.save_text_to_file(
                path_missing_image,
                f"{image_data['pageid']:010d} > {image_data['title']}",
                append=True
            )
            continue

        else:
            NewtUtil.check_dict_keys(
                image_data, {"missing", "ns", "title", "imagerepository"},
                location="mwparser.restructure_json_savefiles : image_data without pageid"
            )

            NewtFiles.save_text_to_file(
                path_missing_image,
                f"Unknown > {image_data['title']}",
                append=True
            )
            continue

        for image_info in image_data["imageinfo"]:
            NewtUtil.check_dict_keys(
                image_info, {"url", "descriptionurl", "descriptionshorturl"},
                location="mwparser.restructure_json_savefiles : image_info"
            )

            url_filename = os.path.basename(image_info["url"])
            filename = f"{image_data['pageid']:010d}-{url_filename}"
            path_file_image = os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FOLDER_RAW_IMAGES, filename)

            if not NewtNet.fetch_data_from_url(
                image_info["url"],
                save_path=path_file_image,
                max_mb_size=SETTING_IMAGE_MAX_MB_SIZE,
                mode="auto",
                repeat_on_fail=False,
                print_log=PRINT_LOG
            ):
                NewtFiles.save_text_to_file(
                    path_missing_image,
                    f"{image_info['url']} > {path_file_image}",
                    append=True
                )
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

    global g_wiki_list_type

    try:
        while True:
            match g_wiki_list_type:
                case "allpages":
                    if "continue" not in json_data:
                        break

                    NewtUtil.check_dict_keys(
                        json_data["continue"], {"apcontinue", "continue"},
                        location="mwparser.loop_next_pages : json_data[continue]"
                    )

                    json_data = get_json_from_url(
                        continue_page_wiki = json_data["continue"]["apcontinue"],
                        continue_page_backup = continue_page_backup
                        )

                    data_list, continue_page_backup = restructure_json_allpages(json_data)
                    save_data_list(data_list)

                case "pageids" | "pagesrecent":
                    if json_data == {}:
                        break

                    if "query" not in json_data:
                        break

                    restructure_json_pageids(json_data)
                    json_data = get_json_from_url()

                case "recentchanges":
                    if "continue" not in json_data:
                        break

                    NewtUtil.check_dict_keys(
                        json_data["continue"], {"rccontinue", "continue"},
                        location="mwparser.loop_next_pages : json_data[continue]"
                    )

                    json_data = get_json_from_url(
                        continue_page_wiki = json_data["continue"]["rccontinue"]
                    )

                    data_list = restructure_json_recentchanges(json_data)
                    save_data_list(data_list)

                case "savefiles":
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

    NewtCons.validate_type(
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
    if SAVE_LOG:
        SETUP_LOGGING_DATA = NewtFiles.setup_logging(DIR_GLOBAL)

    NewtCons.check_location(DIR_GLOBAL, MUST_LOCATION)

    TODO_LIST = check_todo()
    SETTINGS = read_config()
    headers_params_for_url = prep_headers_params_for_url()
    BLOCKED_SET = get_blocked_set()
    json_data = get_json_from_url()

    try:
        match g_wiki_list_type:
            case "allpages":
                data_list, continue_page_backup = restructure_json_allpages(json_data)
                save_data_list(data_list, False)
                loop_next_pages(json_data, continue_page_backup)
                remove_duplicated_lines()

            case "pageids" | "pagesrecent" | "savefiles":
                loop_next_pages(json_data)

            case "recentchanges":
                data_list = restructure_json_recentchanges(json_data)
                save_data_list(data_list, False)
                loop_next_pages(json_data)
                remove_duplicated_lines()

            case _:
                NewtCons.error_msg(
                    f"Unexpected config type: {g_wiki_list_type}",
                    location="mwparser.main : g_wiki_list_type default case"
                )
    except KeyboardInterrupt:
        print()
        print("=== Script interrupted by user ===")

    if SAVE_LOG:
        if g_wiki_list_type in (
                "allpages",
                "pageids",
                ):
            file_target_name = f"{g_wiki_list_type}-{g_namespace_nr_int:0{SETTINGS['ns_max_key_len']}d}.txt"
        else:
            file_target_name = f"{g_wiki_list_type}.txt"

        path_target = os.path.join(DIR_GLOBAL, SETTINGS["FOLDER_LINK"], FOLDER_LOGS, file_target_name)

    print("=== ✅ END ✅ ===")

    if SAVE_LOG:
        NewtFiles.cleanup_logging(SETUP_LOGGING_DATA, path_target)
