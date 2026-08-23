import os

MUST_LOCATION = os.path.join("D:\\", "VS_Code")

BACK_IN_TIME_DAYS = 7

SELECT_CONFIG_FROM_FOLDER = True
# SELECT_CONFIG_FROM_FOLDER = False

# If SELECT_CONFIG_FROM_FOLDER is False, set g_file_config here
DEFAULT_CONFIG_FILE = "xxx.json"
# dev-parser-mediawiki\mwparser\configs\xxx.json

SELECT_WIKI_LIST_TYPE = True
# SELECT_WIKI_LIST_TYPE = False

# If SELECT_WIKI_LIST_TYPE is False, set g_wiki_list_type index here
# "1": "allpages"
# "2": "pageids"
# "3": "recentchanges"
# "4": "pagesrecent"
# "5": "savefiles"
DEFAULT_WIKI_LIST_TYPE = "1"

SELECT_NAMESPACE_NR = True
# SELECT_NAMESPACE_NR = False

# If SELECT_NAMESPACE_NR is False, set g_namespace_nr here
DEFAULT_NAMESPACE_NR = 0

# If ALLPAGES_APCONTINUE_PARAM is not empty, set apcontinue value here
# Extended functionality in prep_params_for_url()
# params.update({"apcontinue": ALLPAGES_APCONTINUE_PARAM})
ALLPAGES_APCONTINUE_PARAM = ""
# Be sure it does not affect next namespace if forgotten to reset values
ALLPAGES_APCONTINUE_NS = None

DELETE_FOLDERS = True
# DELETE_FOLDERS = False

BATCH_START_INDEX_DEFAULT = 0

# max 50 pages per MediaWiki Settings for no admin users
BATCH_MAX_PAGE_IDS = 50
# in get_json_from_url()

# max 25 titles per MediaWiki Settings for no admin users
# 20 helps to avoid too long urls
BATCH_MAX_IMAGE_TITLES = 20
# in get_json_from_url()

# max 2 MB for images to avoid downloading very large files that may cause issues
IMAGE_DOWNLOAD_MAX_MB = 2
# in restructure_json_savefiles()

# PRINT_LOG = True
PRINT_LOG = False

SAVE_LOG = True
# SAVE_LOG = False

# FETCH_MODE = "auto"
FETCH_MODE = "alert"
# FETCH_MODE = "manual"
