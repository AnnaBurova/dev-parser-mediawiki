"""
Updated on 2026-06
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

# TODO: check on config
import script_config as _config

# ==============================================================================

DIR_PROJECT = os.path.dirname(os.path.realpath(__file__))
# print("DIR_PROJECT:", DIR_PROJECT)
# D:\VS_Code\dev-parser-mediawiki\mwparser

DIR_GLOBAL = os.path.dirname(os.path.dirname(DIR_PROJECT))
# print("DIR_GLOBAL: ", DIR_GLOBAL)
# D:\VS_Code

# Add the project root directory to sys.path
sys.path.append(DIR_GLOBAL)

print("MUST_LOCATION:", _config.MUST_LOCATION)
# D:\VS_Code

# ==============================================================================

TIME_NOW = datetime.now(timezone.utc)
time_start = TIME_NOW - timedelta(days=0, hours=0)
TIME_START = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")
time_end = TIME_NOW - timedelta(days=_config.BACK_IN_TIME_DAYS, hours=0)
TIME_END = time_end.strftime("%Y-%m-%dT%H:%M:%SZ")

# ==============================================================================

FOLDER_PROJECT_CONFIGS = os.path.join(DIR_PROJECT, "configs")
FOLDER_RAW_PAGES = os.path.join("data", "raw", "pages")
FOLDER_RAW_REDIRECT = os.path.join("data", "raw", "redirect")
FOLDER_RAW_REMOVED = os.path.join("data", "raw", "removed")
FOLDER_RAW_IMAGES = os.path.join("data", "raw", "images")
FOLDER_LOGS = os.path.join("data", "logs")
FOLDER_LISTS = os.path.join("data", "lists")
FILE_LISTS_BLOCKED = os.path.join(FOLDER_LISTS, "blocked.txt")
FILE_LISTS_RECENTCHANGES = os.path.join(FOLDER_LISTS, "recentchanges.csv")
FILE_SCHEMAS_NAMESPACES = os.path.join("data", "schemas", "namespace_types.json")

# ==============================================================================

NewtFiles.check_file_exists(
    os.path.join(FOLDER_PROJECT_CONFIGS, _config.DEFAULT_CONFIG_FILE)
)

if len(sys.argv) > 1 and sys.argv[1]:
    g_file_config: str = sys.argv[1]
    NewtFiles.check_file_exists(
        os.path.join(FOLDER_PROJECT_CONFIGS, g_file_config)
    )
    SELECT_CONFIG_FROM_FOLDER = False
else:
    # g_file_config = NewtFiles.choose_file_from_folder() in read_current_config()
    g_file_config: str = _config.DEFAULT_CONFIG_FILE
    SELECT_CONFIG_FROM_FOLDER = _config.SELECT_CONFIG_FROM_FOLDER

# ==============================================================================

WIKI_LIST_TYPE_DICT = {
    "1": "allpages",
    "2": "pageids",
    "3": "recentchanges",
    "4": "pagesrecent",
    "5": "savefiles",
}

# get arg 2 safely
sys_arg_wiki_list = sys.argv[2] if len(sys.argv) > 2 else None

if sys_arg_wiki_list and sys_arg_wiki_list in WIKI_LIST_TYPE_DICT:
    g_wiki_list_type: str = WIKI_LIST_TYPE_DICT[sys_arg_wiki_list]
    SELECT_WIKI_LIST_TYPE = False
else:
    if _config.DEFAULT_WIKI_LIST_TYPE not in WIKI_LIST_TYPE_DICT:
        NewtCons.error_msg(
            f"WIKI_LIST_TYPE_DICT.keys: {WIKI_LIST_TYPE_DICT.keys()}",
            location="mwparser.global : DEFAULT_WIKI_LIST_TYPE"
        )
    # g_wiki_list_type = NewtUtil.select_from_input() in read_current_config()
    g_wiki_list_type: str = WIKI_LIST_TYPE_DICT[_config.DEFAULT_WIKI_LIST_TYPE]
    SELECT_WIKI_LIST_TYPE = _config.SELECT_WIKI_LIST_TYPE

# ==============================================================================

if len(sys.argv) > 3 and sys.argv[3]:
    try:
        g_namespace_nr: int = int(sys.argv[3])
    except ValueError as e:
        NewtCons.error_msg(
            f"ValueError: {e}",
            location="mwparser.global : g_namespace_nr"
        )
    SELECT_NAMESPACE_NR = False
else:
    # g_namespace_nr = NewtUtil.select_from_input() in read_current_config()
    g_namespace_nr: int = _config.DEFAULT_NAMESPACE_NR
    SELECT_NAMESPACE_NR = _config.SELECT_NAMESPACE_NR

# Need for global scope
g_namespace_types: dict = {}

# ==============================================================================

if _config.ALLPAGES_APCONTINUE_NS:
    NewtCons.error_msg(
        f" !!! DON'T FORGET ABOUT ALLPAGES_APCONTINUE_NS = {_config.ALLPAGES_APCONTINUE_NS} !!! ",
        location="ALLPAGES_APCONTINUE_NS",
        stop=False
    )
    input("OK?")

# ==============================================================================

# in read_current_config()
if _config.BATCH_START_INDEX_DEFAULT > 0:
    NewtCons.error_msg(
        f" !!! DON'T FORGET ABOUT BATCH_START_INDEX_DEFAULT = {_config.BATCH_START_INDEX_DEFAULT} !!! ",
        location="BATCH_START_INDEX_DEFAULT",
        stop=False
    )
    input("OK?")

# ==============================================================================


def remove_gremlins_from_names(
        page_title
        ) -> str:

    replacements = {
        "_": " ",
        "$": "%24",
        "&": "%26",
        "=": "%3D",
        "\\": "%5C",
        "\xad": "%C2%AD",       # soft hyphen
        "\u0060": "%60",        # grave accent
        "\u00a8": "%C2%A8",     # diaeresis
        "\u00b2": "%C2%B2",     # superscript two
        "\u00b4": "%C2%B4",     # acute accent
        "\u00b5": "%C2%B5",     # micro sign
        "\u200b": "%E2%80%8B",  # zero width space
        "\u2013": "%E2%80%93",  # en dash
        "\u2014": "%E2%80%94",  # em dash
        "\u201c": "%E2%80%9C",  # left double quotation mark
        "\u201d": "%E2%80%9D",  # right double quotation mark
        "\u2020": "%E2%80%A0",  # cross
        "\u205e": "%E2%81%9E",  # vertical four dots
        "\u2117": "%E2%84%97",  # sound recording copyright
        "\u2022": "%E2%80%A2",  # bullet
        "\u2265": "%E2%89%A5",  # greater-than or equal to
        "\u2122": "%E2%84%A2",  # trademark
        "\u2212": "%E2%88%92",  # minus sign
        "\u256d": "%E2%95%AD",  # box drawing light arc down and right
        "\u256e": "%E2%95%AE",  # box drawing light arc down and left
        "\u2606": "%E2%98%86",  # white star
        "\u263a": "%E2%98%BA",  # smiling face
        "\u2665": "%E2%99%A5",  # black heart suit
        "\uff21": "%EF%BC%A1",  # fullwidth A
        "\uff25": "%EF%BC%A5",  # fullwidth E
        "\uff28": "%EF%BC%A8",  # fullwidth H
        "\uff29": "%EF%BC%A9",  # fullwidth I
        "\uff2d": "%EF%BC%AD",  # fullwidth M
        "\uff2f": "%EF%BC%AF",  # fullwidth O
        "\uff33": "%EF%BC%B3",  # fullwidth S
        "\uff34": "%EF%BC%B4",  # fullwidth T
        "\uff37": "%EF%BC%B7",  # fullwidth W
    }

    for old, new in replacements.items():
        page_title = page_title.replace(old, new)

    page_title = page_title.replace("\xad", "%C2%AD")
    page_title = page_title.replace("\u200b", "%E2%80%8B")
    return page_title


def fetch_data_from_mediawiki(
        base_url: str,
        additional_params: dict[str, str]
        ) -> str | bool:

    headers: dict[str, str] = {
        "User-Agent": "MyGuildWarsBot/1.5 (burova.anna+mwparser@gmail.com)",
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

    print()
    data_from_url = NewtNet.fetch_data_from_url(
        base_url,
        headers,
        params,
        mode=_config.FETCH_MODE,
        print_log=_config.PRINT_LOG
    )
    print()

    return data_from_url


def create_namespace_types_file(
        base_url: str,
        file_namespace_types: str
        ) -> None:

    namespace_types_params: dict[str, str] = {
        "meta": "siteinfo",
        "siprop": "namespaces",
    }

    data_from_url = fetch_data_from_mediawiki(base_url, namespace_types_params)
    NewtCons.validate_type(
        data_from_url, str, check_non_empty=True,
        location="mwparser.create_namespace_types_file : data_from_url"
    )
    assert isinstance(data_from_url, str)  # for type checker

    data_json = NewtFiles.convert_str_to_json(data_from_url)
    NewtCons.validate_type(
        data_json, dict, check_non_empty=True,
        location="mwparser.create_namespace_types_file : data_json"
    )
    assert isinstance(data_json, dict)  # for type checker

    NewtUtil.check_dict_keys(
        data_json, {"batchcomplete", "query"},
        location="mwparser.create_namespace_types_file : data_json"
    )

    NewtUtil.check_dict_keys(
        data_json["query"], {"namespaces"},
        location="mwparser.create_namespace_types_file : data_json[query]"
    )

    json_query_namespaces = {}
    for ns_nr, ns_data in data_json["query"]["namespaces"].items():

        if int(ns_nr) < 0:
            continue

        if ns_data["name"] == "":
            ns_data["name"] = "Main"
        if ns_data["name"] == "Talk":
            ns_data["name"] = "Main Talk"

        if all(key in ns_data for key in [
                "canonical",
                "namespaceprotection",
                "defaultcontentmodel",
                ]):
            NewtUtil.check_dict_keys(
                ns_data, {
                    "id", "case", "name", "subpages", "content", "nonincludable",
                    "canonical", "namespaceprotection", "defaultcontentmodel"
                },
                location="mwparser.create_namespace_types_file : data_json[query][namespaces]"
                    + " + namespaceprotection + defaultcontentmodel"
            )

        elif all(key in ns_data for key in [
                "canonical",
                "namespaceprotection",
                ]):
            NewtUtil.check_dict_keys(
                ns_data, {
                    "id", "case", "name", "subpages", "content", "nonincludable",
                    "canonical", "namespaceprotection"
                },
                location="mwparser.create_namespace_types_file : data_json[query][namespaces]"
                    + " + namespaceprotection"
            )

        elif all(key in ns_data for key in [
                "canonical",
                "defaultcontentmodel",
                ]):
            NewtUtil.check_dict_keys(
                ns_data, {
                    "id", "case", "name", "subpages", "content", "nonincludable",
                    "canonical", "defaultcontentmodel"
                },
                location="mwparser.create_namespace_types_file : data_json[query][namespaces]"
                    + " + defaultcontentmodel"
            )

        elif "canonical" in ns_data:
            NewtUtil.check_dict_keys(
                ns_data, {
                    "id", "case", "name", "subpages", "content", "nonincludable",
                    "canonical"
                },
                location="mwparser.create_namespace_types_file : data_json[query][namespaces]"
                    + " + canonical"
            )

        else:
            NewtUtil.check_dict_keys(
                ns_data, {"id", "case", "name", "subpages", "content", "nonincludable"},
                location="mwparser.create_namespace_types_file : data_json[query][namespaces]"
                    + " + else"
            )
            json_query_namespaces[str(ns_nr)] = ns_data["name"]
            continue

        if ns_data["canonical"] == "":
            ns_data["canonical"] = "Main"
        if ns_data["canonical"] == "Talk":
            ns_data["canonical"] = "Main Talk"

        if ns_data["name"] == ns_data["canonical"]:
            json_query_namespaces[str(ns_nr)] = ns_data["name"]
        else:
            json_query_namespaces[str(ns_nr)] = f"{ns_data["name"]} ({ns_data["canonical"]})"

    NewtFiles.save_json_to_file(file_namespace_types, json_query_namespaces)


def create_todo_list(
        ) -> list[tuple[str, str, str | None, str | None]]:

    todo_list: list[tuple[str, str, str | None, str | None]] = []

    for proj_config in os.listdir(FOLDER_PROJECT_CONFIGS):
        file_config = os.path.join(FOLDER_PROJECT_CONFIGS, proj_config)

        # Skip if it's not a file (e.g., directory)
        if not os.path.isfile(file_config):
            continue

        # Skip non-config files
        if not proj_config.endswith(".json"):
            NewtCons.error_msg(
                f"Found non-config file: {proj_config}",
                f"Folder: {FOLDER_PROJECT_CONFIGS}",
                location="mwparser.create_todo_list : proj_config not endswith(json)"
            )
            continue

        # Skip specific config example file
        if proj_config == "xxx.json":
            continue

        # Get settings from config file
        proj_settings = NewtFiles.read_json_from_file(file_config, print_log=_config.PRINT_LOG)
        NewtCons.validate_type(
            proj_settings, dict, check_non_empty=True,
            location="mwparser.create_todo_list : proj_settings"
        )
        assert isinstance(proj_settings, dict)  # for type checker

        # Check required keys in proj_settings
        NewtUtil.check_dict_keys(
            proj_settings, {"FOLDER_LINK", "BASE_URL"},
            location="mwparser.create_todo_list : proj_settings"
        )

        for setting_value in proj_settings.values():
            NewtCons.validate_type(
                setting_value, str, check_non_empty=True,
                location="mwparser.create_todo_list : proj_settings[setting_value]"
            )

        # Check if namespace_types.json exists for the config
        file_namespace_types = os.path.join(
            DIR_GLOBAL, proj_settings["FOLDER_LINK"], FILE_SCHEMAS_NAMESPACES
        )

        if not NewtFiles.check_file_exists(file_namespace_types, stop=False):
            create_namespace_types_file(proj_settings["BASE_URL"], file_namespace_types)

        if not os.path.isfile(file_namespace_types):
            NewtCons.error_msg(
                f"Missing namespace_types.json for config: {proj_config}",
                f"File must be here: {file_namespace_types}",
                location="mwparser.create_todo_list : namespace_types.json missing"
            )

        # Get namespace types from file
        namespace_dict = NewtFiles.read_json_from_file(file_namespace_types, print_log=_config.PRINT_LOG)
        NewtCons.validate_type(
            namespace_dict, dict, check_non_empty=True,
            location="mwparser.create_todo_list : namespace_dict"
        )
        assert isinstance(namespace_dict, dict)  # for type checker

        # Calculate max key length from namespace types for formatting
        ns_max_key_len = len(max(namespace_dict.keys(), key=len))

        # Check folder with logs to find missing logs for todo
        folder_with_logs = os.path.join(
            DIR_GLOBAL, proj_settings["FOLDER_LINK"], FOLDER_LOGS
        )

        # Check if each wiki list type has log file
        for wiki_list_type in WIKI_LIST_TYPE_DICT.values():
            # This types has sub log for each namespace
            if wiki_list_type in (
                    "allpages",
                    "pageids",
                    ):
                for ns_key, ns_value in namespace_dict.items():
                    file_wiki_log = f"{wiki_list_type}-{int(ns_key):0{ns_max_key_len}d}.txt"
                    path_wiki_log = os.path.join(folder_with_logs, file_wiki_log)
                    if not os.path.isfile(path_wiki_log):
                        todo_list.append((proj_config, wiki_list_type, ns_key, ns_value))

            # Other types dont have sub logs, only 1
            else:
                path_wiki_log = os.path.join(folder_with_logs, f"{wiki_list_type}.txt")
                if not os.path.isfile(path_wiki_log):
                    todo_list.append((proj_config, wiki_list_type, None, None))

    if todo_list and _config.PRINT_LOG:
        print()
        print("=== TODO LIST ===")
        todo_list.reverse()
        for todo in todo_list:
            print(todo)

    return todo_list


def read_current_config(
        todo_list: list[tuple[str, str, str | None, str | None]]
        ) -> dict:

    global g_file_config
    global g_wiki_list_type
    global g_namespace_types
    global g_namespace_nr

    # --------------------------------------------------------------------------
    # Select WIKI Project
    # Settings are at file beginning of script
    if SELECT_CONFIG_FROM_FOLDER:
        count_file_config = NewtUtil.count_values_by_position(
            todo_list,
            position = 0
        )

        g_file_config = NewtFiles.choose_file_from_folder(
            FOLDER_PROJECT_CONFIGS,
            count_file_config
        )

    # Get settings content from config file
    # Its structure is already checked in create_todo_list() function
    # And file exists, so we can be sure it has all required keys and values
    path_config_file = os.path.join(FOLDER_PROJECT_CONFIGS, g_file_config)

    settings = NewtFiles.read_json_from_file(path_config_file, print_log=_config.PRINT_LOG)
    NewtCons.validate_type(
        settings, dict, check_non_empty=True,
        location="mwparser.read_current_config : settings"
    )
    assert isinstance(settings, dict)  # for type checker

    # --------------------------------------------------------------------------
    # Select WIKI Data Type
    if SELECT_WIKI_LIST_TYPE:
        count_wiki_list_types = NewtUtil.count_values_by_position(
            [todo for todo in todo_list if todo[0] == g_file_config],
            position = 1
        )

        wiki_list_type_nr = NewtUtil.select_from_input(WIKI_LIST_TYPE_DICT, count_wiki_list_types)
        NewtCons.validate_type(
            wiki_list_type_nr, str, check_non_empty=True,
            location="mwparser.read_current_config : wiki_list_type_nr"
        )
        assert isinstance(wiki_list_type_nr, str)  # for type checker

        g_wiki_list_type = WIKI_LIST_TYPE_DICT[wiki_list_type_nr]

    # --------------------------------------------------------------------------
    # Put namespace types into global scope
    json_namespace_types = NewtFiles.read_json_from_file(
        os.path.join(DIR_GLOBAL, settings["FOLDER_LINK"], FILE_SCHEMAS_NAMESPACES),
        print_log=_config.PRINT_LOG
    )
    NewtCons.validate_type(
        json_namespace_types, dict, check_non_empty=True,
        location="mwparser.read_current_config : json_namespace_types"
    )
    assert isinstance(json_namespace_types, dict)  # for type checker

    g_namespace_types = json_namespace_types

    # --------------------------------------------------------------------------
    # Select Namespace Number if needed (for types with multiple namespaces)
    if g_wiki_list_type in (
            "allpages",
            "pageids",
            ):
        if SELECT_NAMESPACE_NR:
            count_namespace_types = NewtUtil.count_values_by_position(
                [todo for todo in todo_list
                if todo[0] == g_file_config and todo[1] == g_wiki_list_type],
                position = 3
            )

            namespace_types_nr = NewtUtil.select_from_input(g_namespace_types, count_namespace_types)

            NewtCons.validate_type(
                namespace_types_nr, str, check_non_empty=True,
                location="mwparser.read_current_config : namespace_types_nr"
            )
            assert isinstance(namespace_types_nr, str)  # for type checker
            g_namespace_nr = int(namespace_types_nr)

    # Calculate max key length from namespace types for formatting
    settings["ns_max_key_len"] = len(max(g_namespace_types.keys(), key=len))

    # --------------------------------------------------------------------------
    # Set index start for batch results
    if g_wiki_list_type in (
            "pageids",
            "pagesrecent",
            "savefiles",
            ):
        settings["index_start"] = _config.BATCH_START_INDEX_DEFAULT

    # --------------------------------------------------------------------------
    # Get Page IDs from allpages
    if g_wiki_list_type == "pageids":
        if _config.BATCH_START_INDEX_DEFAULT == 0 and _config.DELETE_FOLDERS:
            for folder_type in (FOLDER_RAW_PAGES, FOLDER_RAW_REDIRECT, FOLDER_RAW_REMOVED):
                folder_to_remove = os.path.join(
                    DIR_GLOBAL,
                    settings["FOLDER_LINK"],
                    folder_type,
                    f"{g_namespace_nr:0{settings['ns_max_key_len']}d}"
                )
                if os.path.isdir(folder_to_remove):
                    print(f"Removing folder: {folder_to_remove}")
                    shutil.rmtree(folder_to_remove)
                    print()

        path_allpages = os.path.join(
            DIR_GLOBAL, settings["FOLDER_LINK"], FOLDER_LISTS,
            "allpages", f"{g_namespace_nr:0{settings['ns_max_key_len']}d}.csv"
        )
        list_allpages = NewtFiles.read_csv_from_file(path_allpages)
        NewtCons.validate_type(
            list_allpages, list, check_non_empty=True,
            location="mwparser.read_current_config : list_allpages"
        )
        assert isinstance(list_allpages, list)  # for type checker

        # skip header and get only ids from first column
        settings["page_ids"] = sorted([int(row[0]) for row in list_allpages[1:]])

    # --------------------------------------------------------------------------
    # Get Page IDs from recentchanges
    elif g_wiki_list_type == "pagesrecent":
        path_recentchanges = os.path.join(
            DIR_GLOBAL, settings["FOLDER_LINK"], FILE_LISTS_RECENTCHANGES
        )
        list_recentchanges = NewtFiles.read_csv_from_file(path_recentchanges)
        NewtCons.validate_type(
            list_recentchanges, list, check_non_empty=True,
            location="mwparser.read_current_config : list_recentchanges"
        )
        assert isinstance(list_recentchanges, list)  # for type checker

        # skip header and get only ids from second column, filter out 0, check unique and sort
        settings["page_ids"] = sorted(list(set(
            [int(row[1]) for row in list_recentchanges[1:] if int(row[1]) > 0]
        )))

    # --------------------------------------------------------------------------
    # Get Page IDs for Files from allpages
    elif g_wiki_list_type == "savefiles":
        g_namespace_nr = 6  # Standard Files Namespace

        path_allpages = os.path.join(
            DIR_GLOBAL, settings["FOLDER_LINK"], FOLDER_LISTS,
            "allpages", f"{g_namespace_nr:0{settings['ns_max_key_len']}d}.csv"
        )
        list_files = NewtFiles.read_csv_from_file(path_allpages)
        NewtCons.validate_type(
            list_files, list, check_non_empty=True,
            location="mwparser.read_current_config : list_files"
        )
        assert isinstance(list_files, list)  # for type checker

        # skip header and get only file titles from second column
        settings["files_titles"] = sorted([str(row[1]) for row in list_files[1:]])

    return settings


def prep_params_for_url(
        ) -> dict:

    params = {}

    match g_wiki_list_type:
        case "allpages":
            params.update({"list": "allpages"})
            params.update({"aplimit": "max"})
            params.update({"apnamespace": str(g_namespace_nr)})

            if _config.ALLPAGES_APCONTINUE_PARAM and _config.ALLPAGES_APCONTINUE_NS == g_namespace_nr:
                params.update({"apcontinue": _config.ALLPAGES_APCONTINUE_PARAM})

        case "pageids":
            params.update({"prop": "revisions"})
            params.update({"rvprop": "content"})
            params.update({"rvslots": "*"})

        case "recentchanges":
            params.update({"list": "recentchanges"})
            params.update({"rcnamespace": "*"})
            params.update({"rclimit": "max"})
            params.update({"rcstart": str(TIME_START)})
            params.update({"rcend": str(TIME_END)})

        case "pagesrecent":
            params.update({"prop": "revisions"})
            params.update({"rvprop": "content"})
            params.update({"rvslots": "*"})

        case "savefiles":
            params.update({"maxlag": "5"})
            params.update({"prop": "imageinfo"})
            params.update({"iiprop": "url"})

        case _:
            NewtCons.error_msg(
                f"Unexpected config type: {g_wiki_list_type}",
                location="mwparser.prep_params_for_url : g_wiki_list_type default case"
            )

    return params


def get_blocked_set(
        settings: dict[str, str]
        ) -> set[str]:

    blocked_set = set()
    path_file_blocked = os.path.join(DIR_GLOBAL, settings["FOLDER_LINK"], FILE_LISTS_BLOCKED)

    if not NewtFiles.check_file_exists(path_file_blocked, stop=False):
        NewtFiles.save_text_to_file(
            path_file_blocked,
            "",
            append=False,
            print_log=_config.PRINT_LOG
        )

    blocked_list = NewtFiles.read_text_from_file(path_file_blocked, print_log=_config.PRINT_LOG)

    if blocked_list:
        for line in blocked_list.splitlines():
            line = line.strip()
            if line and not line.startswith("!"):
                blocked_set.add(line)

    return blocked_set


def get_json_from_url(
        settings: dict[str, str],
        additional_params: dict[str, str]
        ) -> dict:

    path_file_blocked = os.path.join(DIR_GLOBAL, settings["FOLDER_LINK"], FILE_LISTS_BLOCKED)

    if g_wiki_list_type in (
            "pageids",
            "pagesrecent",
            ):
        if len(settings["page_ids"]) == 0:
            print()
            print("No pages to process. Empty list.")
            return {}

        index_start = int(settings["index_start"])
        index_max = _config.BATCH_MAX_PAGE_IDS
        index_end = index_start + index_max

        if len(settings["page_ids"]) < index_start:
            print()
            print("No more pages to process. Done.")
            return {}

        if len(settings["page_ids"][index_start:index_end]) == 0:
            print()
            print("No more pages to process. Done.")
            return {}

        additional_params.update({"pageids": "|".join(
            map(str, settings["page_ids"][index_start:index_end])
        )})

        settings["index_start"] = str(index_end)

        print()
        print(f"Processing page IDs from index {index_start} to {index_end}")
        print(f"    Max index: {len(settings['page_ids'])}")
        print(f"Processing current page: {index_start / index_max}")
        print(f"    Max pages: {len(settings['page_ids']) / index_max}")

    elif g_wiki_list_type == "savefiles":
        if len(settings["files_titles"]) == 0:
            print()
            print("No images to process. Empty list.")
            return {}

        index_start = int(settings["index_start"])
        index_max = _config.BATCH_MAX_IMAGE_TITLES
        index_end = index_start + index_max

        if len(settings["files_titles"]) < index_start:
            print()
            print("No more images to process. Done.")
            return {}

        if len(settings["files_titles"][index_start:index_end]) == 0:
            print()
            print("No more images to process. Done.")
            return {}

        additional_params.update({"titles": "|".join(
            map(str, settings["files_titles"][index_start:index_end])
        )})

        settings["index_start"] = str(index_end)

        print()
        print(f"Processing images IDs from index {index_start} to {index_end}")
        print(f"    Max index: {len(settings['files_titles'])}")
        print(f"Processing current page: {index_start / index_max}")
        print(f"    Max pages: {len(settings['files_titles']) / index_max}")

    data_from_url = fetch_data_from_mediawiki(
        settings["BASE_URL"],
        additional_params
    )

    # None data mostly comes from 403 Forbidden error, so we save apcontinue to blocked list and skip it next time
    if data_from_url is False:
        if "apcontinue" in additional_params:
            clean_apcontinue = remove_gremlins_from_names(
                g_namespace_types[str(g_namespace_nr)]+":"+additional_params["apcontinue"]
            )
            NewtFiles.save_text_to_file(
                path_file_blocked,
                clean_apcontinue,
                append=True
            )

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

        match g_wiki_list_type:
            case "pageids" | "pagesrecent":
                for index_range in range(index_start, index_end):
                    if len(settings["page_ids"]) <= index_range:
                        break

                    additional_params.update({"pageids": str(settings["page_ids"][index_range])})

                    data_chunk_from_url = fetch_data_from_mediawiki(
                        settings["BASE_URL"],
                        additional_params
                    )

                    NewtCons.validate_type(
                        data_chunk_from_url, str, check_non_empty=True,
                        location="mwparser.get_json_from_url : data_chunk_from_url"
                    )
                    assert isinstance(data_chunk_from_url, str)  # for type checker

                    json_chunk_from_url = NewtFiles.convert_str_to_json(data_chunk_from_url)

                    if not NewtCons.validate_type(
                        json_chunk_from_url, dict, check_non_empty=True, stop=False,
                        location="mwparser.get_json_from_url : json_chunk_from_url Dict"
                    ):
                        NewtCons.validate_type(
                            json_chunk_from_url, type(None), check_non_empty=True,
                            location="mwparser.get_json_from_url : json_chunk_from_url None"
                        )

                        NewtFiles.save_text_to_file(
                            path_file_blocked,
                            f"!NoneValueChunk:{g_namespace_nr}:{g_namespace_types[str(g_namespace_nr)]} > {additional_params}",
                            append=True
                        )
                        continue

                    assert isinstance(json_chunk_from_url, dict)  # for type checker

                    NewtUtil.check_dict_keys(
                        json_chunk_from_url, {"query", "batchcomplete"},
                        location="mwparser.get_json_from_url : json_chunk_from_url"
                    )

                    NewtUtil.check_dict_keys(
                        json_chunk_from_url["query"], {"pages"},
                        location="mwparser.get_json_from_url : json_chunk_from_url[query]"
                    )

                    data_from_url_chunks["query"]["pages"].extend(
                        json_chunk_from_url.get("query", {}).get("pages", [])
                    )

                json_from_url = data_from_url_chunks

            case _:
                NewtCons.error_msg(
                    f"Unexpected config type: {g_wiki_list_type}",
                    location="mwparser.get_json_from_url : g_wiki_list_type default case"
                )

    NewtCons.validate_type(
        json_from_url, dict, check_non_empty=True,
        location="mwparser.get_json_from_url : json_from_url"
    )
    assert isinstance(json_from_url, dict)  # for type checker

    return json_from_url


def restructure_json_allpages(
        json_data: dict,
        blocked_set: set
        ) -> tuple[list[list[str]], str]:

    if "continue" in json_data:
        NewtUtil.check_dict_keys(
            json_data, {"query", "batchcomplete", "limits", "continue"},
            location="mwparser.restructure_json_allpages : json_data + continue"
        )

    else:
        NewtUtil.check_dict_keys(
            json_data, {"query", "batchcomplete", "limits"},
            location="mwparser.restructure_json_allpages : json_data no continue"
        )

    NewtUtil.check_dict_keys(
        json_data["query"], {"allpages"},
        location="mwparser.restructure_json_allpages : json_data[query]"
    )

    title_backup = ""
    allpages_list = []
    allpages_list.append(["pageid", "title"])
    for page in json_data["query"]["allpages"]:
        NewtUtil.check_dict_keys(
            page, {"pageid", "ns", "title"},
            location="mwparser.restructure_json_allpages : page"
        )

        if int(page["ns"]) != g_namespace_nr:
            NewtCons.error_msg(
                f"Unexpected namespace value: {page['ns']} for page ID {page['pageid']}",
                f"Page: {page}",
                location="mwparser.restructure_json_allpages : page[ns]"
            )

        if g_namespace_types[str(g_namespace_nr)] == "Main":
            page["title"] = "Main:"+page["title"]
        if g_namespace_types[str(g_namespace_nr)] == "Main Talk":
            page["title"] = "Main "+page["title"]

        if remove_gremlins_from_names(page["title"]) in blocked_set:
            continue

        title_backup = page["title"]

        allpages_list.append([f"{page['pageid']:010d}", remove_gremlins_from_names(page["title"])])

    return (allpages_list, title_backup)


def restructure_json_pageids(
        json_data: dict,
        settings: dict
        ) -> None:

    NewtUtil.check_dict_keys(
        json_data, {"query", "batchcomplete"},
        location="mwparser.restructure_json_pageids : json_data"
    )

    NewtUtil.check_dict_keys(
        json_data["query"], {"pages"},
        location="mwparser.restructure_json_pageids : json_data[query]"
    )

    for page in json_data["query"]["pages"]:
        if "missing" in page and page["missing"] is True:
            NewtUtil.check_dict_keys(
                page, {"pageid", "missing"},
                location="mwparser.restructure_json_pageids : missing"
            )
            path_file_blocked = os.path.join(DIR_GLOBAL, settings["FOLDER_LINK"], FILE_LISTS_BLOCKED)
            NewtFiles.save_text_to_file(
                path_file_blocked,
                f"!MissingPageid:{g_namespace_nr}:{g_namespace_types[str(g_namespace_nr)]} > {page['pageid']}",
                append=True
            )
            continue

        NewtUtil.check_dict_keys(
            page, {"pageid", "ns", "title", "revisions"},
            location="mwparser.restructure_json_pageids : page"
        )

        check_namespace_nr = g_namespace_nr

        if g_wiki_list_type == "pagesrecent":
            if str(page["ns"]) in g_namespace_types:
                check_namespace_nr = int(page["ns"])

        if int(page["ns"]) != check_namespace_nr:
            NewtCons.error_msg(
                f"Unexpected namespace value: {page['ns']} for page ID {page['pageid']}",
                f"Page: {page}",
                location="mwparser.restructure_json_pageids : page[ns]"
            )

        # Basic path for files to save
        folder_pages = FOLDER_RAW_PAGES

        text_for_file = ""
        text_for_file += f"Namespace ::: {page['ns']} ::: {g_namespace_types[str(page['ns'])]}\n"
        text_for_file += f"Page ID   ::: {page['pageid']}\n"
        text_for_file += f"Title     ::: {page['title']}\n"
        text_for_file += "\n" + "-" * 80 + "\n\n"

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

            text_for_file += f"contentmodel  ::: {revision['slots']['main']['contentmodel']}\n"
            text_for_file += f"contentformat ::: {revision['slots']['main']['contentformat']}\n"
            text_for_file += "\n" + "-" * 80 + "\n\n"

            if len(revision["slots"]["main"]["content"]) == 0:
                folder_pages = FOLDER_RAW_REMOVED

            if revision["slots"]["main"]["content"].strip().lower().startswith("#redirect"):
                folder_pages = FOLDER_RAW_REDIRECT

            text_for_file += f"{revision['slots']['main']['content']}\n"
            text_for_file += "\n" + "-" * 80 + "\n\n"

        text_for_file += "=== END ==="

        formatted_id = f"{page['pageid']:010d}"
        filename = os.path.join(
            f"{formatted_id[0:4]}",
            f"{formatted_id[4:7]}",
            f"{formatted_id}.txt"
        )
        path_file_pageid = os.path.join(
            DIR_GLOBAL,
            settings["FOLDER_LINK"],
            folder_pages,
            f"{g_namespace_nr:0{settings['ns_max_key_len']}d}",
            filename
        )

        NewtFiles.save_text_to_file(
            path_file_pageid,
            text_for_file,
            append=False
        )


def restructure_json_recentchanges(
        json_data: dict,
        settings: dict,
        blocked_set: set
        ) -> list[list[str]]:

    if "continue" in json_data:
        NewtUtil.check_dict_keys(
            json_data, {"query", "batchcomplete", "limits", "continue"},
            location="mwparser.restructure_json_recentchanges : json_data + continue"
        )

    else:
        NewtUtil.check_dict_keys(
            json_data, {"query", "batchcomplete", "limits"},
            location="mwparser.restructure_json_recentchanges : json_data no continue"
        )

    NewtUtil.check_dict_keys(
        json_data["query"], {"recentchanges"},
        location="mwparser.restructure_json_recentchanges : json_data[query]"
    )

    recentchanges_list = []
    recentchanges_list.append(["timestamp", "pageid", "ns", "type", "title"])
    for page in json_data["query"]["recentchanges"]:
        NewtUtil.check_dict_keys(
            page, {"type", "ns", "title", "pageid", "revid", "old_revid", "rcid", "timestamp"},
            location="mwparser.restructure_json_recentchanges : page"
        )

        if str(page["ns"]) not in g_namespace_types:
            NewtCons.error_msg(
                f"Unexpected namespace value: {page['ns']} for page ID {page['title']}",
                f"Page: {page}",
                location="mwparser.restructure_json_recentchanges : page[ns]",
                stop=False
            )

        if g_namespace_types[str(g_namespace_nr)] == "Main":
            page["title"] = "Main:"+page["title"]
        if g_namespace_types[str(g_namespace_nr)] == "Main Talk":
            page["title"] = "Main "+page["title"]

        if page["pageid"] == 0:
            continue

        page["title"] = remove_gremlins_from_names(page["title"])

        if page["title"] in blocked_set:
            continue

        recentchanges_list.append([
            page["timestamp"],
            f"{page['pageid']:010d}",
            f"{page['ns']:0{settings['ns_max_key_len']}d}",
            f"{page['type']:>4}",
            page["title"],
        ])

    return recentchanges_list


def restructure_json_savefiles(
        json_data: dict,
        settings: dict
        ) -> None:

    if "continue" in json_data:
        NewtUtil.check_dict_keys(
            json_data, {"query", "continue"},
            location="mwparser.restructure_json_savefiles : json_data + continue"
        )

    else:
        NewtUtil.check_dict_keys(
            json_data, {"query", "batchcomplete"},
            location="mwparser.restructure_json_savefiles : json_data + batchcomplete"
        )

    NewtUtil.check_dict_keys(
        json_data["query"], {"pages"},
        location="mwparser.restructure_json_savefiles : json_data[query]"
    )

    path_file_blocked = os.path.join(DIR_GLOBAL, settings["FOLDER_LINK"], FILE_LISTS_BLOCKED)

    for image_data in json_data["query"]["pages"]:
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
                path_file_blocked,
                remove_gremlins_from_names(image_data['title']),
                append=True
            )
            continue

        else:
            NewtUtil.check_dict_keys(
                image_data, {"missing", "ns", "title", "imagerepository"},
                location="mwparser.restructure_json_savefiles : image_data without pageid"
            )

            NewtFiles.save_text_to_file(
                path_file_blocked,
                remove_gremlins_from_names(image_data['title']),
                append=True
            )
            continue

        for image_info in image_data["imageinfo"]:
            NewtUtil.check_dict_keys(
                image_info, {"url", "descriptionurl", "descriptionshorturl"},
                location="mwparser.restructure_json_savefiles : image_info"
            )

            url_filename = os.path.basename(image_info["url"])
            formatted_id = f"{image_data['pageid']:010d}"
            filename = os.path.join(f"{formatted_id[0:4]}", f"{formatted_id[4:7]}", f"{formatted_id}-{url_filename}")
            path_file_image = os.path.join(DIR_GLOBAL, settings["FOLDER_LINK"], FOLDER_RAW_IMAGES, filename)

            if not NewtNet.fetch_data_from_url(
                image_info["url"],
                mode=_config.FETCH_MODE,
                save_path=path_file_image,
                max_mb_size=_config.IMAGE_DOWNLOAD_MAX_MB,
                repeat_on_fail=False,
                print_log=_config.PRINT_LOG
            ):
                NewtFiles.save_text_to_file(
                    path_file_blocked,
                    f"!ImageFalse:{g_namespace_nr}:{g_namespace_types[str(g_namespace_nr)]} > {image_info['url']} > {path_file_image}",
                    append=True
                )
            else:
                print()
                print("Local image: ", path_file_image)
        print()


def save_data_list(
        settings: dict,
        data_list: list[list[str]],
        append: bool = True
        ) -> None:

    match g_wiki_list_type:
        case "allpages":
            csv_file_path = os.path.join(
                DIR_GLOBAL,
                settings["FOLDER_LINK"],
                FOLDER_LISTS,
                g_wiki_list_type,
                f"{g_namespace_nr:0{settings['ns_max_key_len']}d}.csv"
            )

        case "recentchanges":
            csv_file_path = os.path.join(
                DIR_GLOBAL,
                settings["FOLDER_LINK"],
                FILE_LISTS_RECENTCHANGES
            )

        case _:
            NewtCons.error_msg(
                f"Unexpected config type: {g_wiki_list_type}",
                location="mwparser.save_data_list : g_wiki_list_type default case"
            )

    NewtFiles.save_csv_to_file(
        csv_file_path,
        data_list,
        append=append,
        print_log=_config.PRINT_LOG
    )


def loop_next_pages(
        json_data: dict,
        blocked_set: set,
        settings: dict[str, str],
        additional_params: dict[str, str],
        title_backup: str
        ) -> None:

    while True:
        match g_wiki_list_type:
            case "allpages":
                if "continue" not in json_data:
                    break

                NewtUtil.check_dict_keys(
                    json_data["continue"], {"apcontinue", "continue"},
                    location="mwparser.loop_next_pages : allpages : json_data[continue]"
                )

                ns_type = g_namespace_types[str(g_namespace_nr)]

                # Only without left and sep parts it will work in continue
                left_part, sep_part, right_part = title_backup.partition(":")
                if sep_part and left_part == ns_type:
                    title_backup = right_part

                check_apcontinue = remove_gremlins_from_names(
                    ns_type+":"+json_data["continue"]["apcontinue"]
                )

                if check_apcontinue in blocked_set and title_backup:
                    additional_params.update({"apcontinue": title_backup})
                else:
                    additional_params.update({"apcontinue": json_data["continue"]["apcontinue"]})

                json_data = get_json_from_url(
                    settings,
                    additional_params
                )

                data_list, title_backup = restructure_json_allpages(json_data, blocked_set)
                save_data_list(settings, data_list)

            case "pageids" | "pagesrecent":
                if json_data == {}:
                    break

                if "query" not in json_data:
                    NewtUtil.check_dict_keys(
                        json_data, {"batchcomplete"},
                        location="mwparser.loop_next_pages : pageids : json_data"
                    )
                    break

                restructure_json_pageids(json_data, settings)

                json_data = get_json_from_url(
                    settings,
                    additional_params
                )

            case "recentchanges":
                if "continue" not in json_data:
                    break

                NewtUtil.check_dict_keys(
                    json_data["continue"], {"rccontinue", "continue"},
                    location="mwparser.loop_next_pages : recentchanges : json_data[continue]"
                )

                additional_params.update({"rccontinue": json_data["continue"]["rccontinue"]})

                json_data = get_json_from_url(
                    settings,
                    additional_params
                )

                data_list = restructure_json_recentchanges(json_data, settings, blocked_set)
                save_data_list(settings, data_list)

            case "savefiles":
                if json_data == {}:
                    break

                restructure_json_savefiles(json_data, settings)
                json_data = get_json_from_url(
                    settings,
                    additional_params
                )

            case _:
                NewtCons.error_msg(
                    f"Unexpected config type: {g_wiki_list_type}",
                    location="mwparser.loop_next_pages : g_wiki_list_type default case"
                )


def sort_and_deduplicate_lines(
        settings: dict,
        ) -> None:

    match g_wiki_list_type:
        case "allpages":
            csv_file_path = os.path.join(
                DIR_GLOBAL,
                settings["FOLDER_LINK"],
                FOLDER_LISTS,
                g_wiki_list_type,
                f"{g_namespace_nr:0{settings['ns_max_key_len']}d}.csv"
            )

        case "recentchanges":
            csv_file_path = os.path.join(
                DIR_GLOBAL,
                settings["FOLDER_LINK"],
                FILE_LISTS_RECENTCHANGES
            )

        case _:
            NewtCons.error_msg(
                f"Unexpected config type: {g_wiki_list_type}",
                location="mwparser.sort_and_deduplicate_lines : g_wiki_list_type default case"
            )

    print()
    csv_lines = NewtFiles.read_csv_from_file(
        csv_file_path,
        print_log=_config.PRINT_LOG
    )
    NewtCons.validate_type(
        csv_lines, list, check_non_empty=True,
        location="mwparser.sort_and_deduplicate_lines : csv_lines"
    )
    assert isinstance(csv_lines, list)  # for type checker

    # Separate header from data
    row_header = csv_lines[0] if csv_lines else []
    rows_data = csv_lines[1:] if len(csv_lines) > 1 else []

    # Ensure header does not exist in data_lines
    data_lines = {tuple(line) for line in rows_data if line != row_header}
    unique_lines = [list(line) for line in sorted(data_lines)]

    # Prepend header back
    sorted_lines = [row_header] + unique_lines

    NewtFiles.save_csv_to_file(
        csv_file_path,
        sorted_lines,
        print_log=_config.PRINT_LOG
    )


def main_func(
        ) -> dict:

    todo_list_tuple = create_todo_list()
    wiki_settings = read_current_config(todo_list_tuple)
    params_for_url = prep_params_for_url()
    blocked_set = get_blocked_set(wiki_settings)
    json_data = get_json_from_url(wiki_settings, params_for_url)

    match g_wiki_list_type:
        case "allpages":
            data_list, title_backup = restructure_json_allpages(json_data, blocked_set)
            save_data_list(wiki_settings, data_list, False)
            loop_next_pages(json_data, blocked_set, wiki_settings, params_for_url, title_backup)
            sort_and_deduplicate_lines(wiki_settings)

        case "pageids" | "pagesrecent" | "savefiles":
            loop_next_pages(json_data, blocked_set, wiki_settings, params_for_url, "")

        case "recentchanges":
            data_list = restructure_json_recentchanges(json_data, wiki_settings, blocked_set)
            save_data_list(wiki_settings, data_list, False)
            loop_next_pages(json_data, blocked_set, wiki_settings, params_for_url, "")
            sort_and_deduplicate_lines(wiki_settings)

        case _:
            NewtCons.error_msg(
                f"Unexpected config type: {g_wiki_list_type}",
                location="mwparser.main_func : g_wiki_list_type default case"
            )

    return wiki_settings


if __name__ == "__main__":
    if _config.SAVE_LOG:
        SETUP_LOGGING_DATA = NewtFiles.setup_logging(DIR_GLOBAL)

    NewtCons.check_location(DIR_GLOBAL, _config.MUST_LOCATION)

    try:
        settings = main_func()

    except KeyboardInterrupt:
        print()
        print("=== Script interrupted by user ===")

    except SystemExit:
        time_error = datetime.now(timezone.utc)
        NewtCons.error_msg(
            "Time stop: " + time_error.strftime("%Y-%m-%d %H:%M:%S"),
            "SystemExit on fetching all pages",
            location="mwparser.main_func : SystemExit"
        )

    print()
    print("=== ✅ END ✅ ===")

    if _config.SAVE_LOG:
        if g_wiki_list_type in (
                "allpages",
                "pageids",
                ):
            path_target = os.path.join(
                DIR_GLOBAL,
                settings["FOLDER_LINK"],
                FOLDER_LOGS,
                f"{g_wiki_list_type}-{g_namespace_nr:0{settings['ns_max_key_len']}d}.txt"
            )
        else:
            path_target = os.path.join(
                DIR_GLOBAL,
                settings["FOLDER_LINK"],
                FOLDER_LOGS,
                f"{g_wiki_list_type}.txt"
            )

        NewtFiles.cleanup_logging(SETUP_LOGGING_DATA, path_target)
