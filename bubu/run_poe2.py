import sys
import os

# import newtutils.console as NewtCons
# import newtutils.utility as NewtUtil
import newtutils.files as NewtFiles
# import newtutils.sql as NewtSQL
# import newtutils.network as NewtNet


def save_csv(input_file, output_file, append):
    start_line = append
    end_line = start_line+99  # inclusive, so this gives exactly 100 lines: 201..300

    lines = NewtFiles.read_csv_from_file(input_file)
    assert isinstance(lines, list)

    result = [lines[0]] + lines[start_line - 1:end_line]
    NewtFiles.save_csv_to_file(output_file, result)


def append_csv(input_file, output_file, append):
    start_line = 0
    end_line = append+99  # inclusive, so this gives exactly 100 lines: 201..300

    lines = NewtFiles.read_csv_from_file(input_file)
    assert isinstance(lines, list)

    result = lines[start_line:end_line]
    NewtFiles.save_csv_to_file(output_file, result)


def copy_log(local_log_file, outside_log_file):
    lines1 = NewtFiles.read_text_from_file(outside_log_file)
    assert isinstance(lines1, str)

    NewtFiles.save_text_to_file(local_log_file, lines1, append=True)

    lines2 = NewtFiles.read_text_from_file(local_log_file)
    assert isinstance(lines2, str)

    NewtFiles.save_text_to_file(outside_log_file, lines2)


# start = "yes"
start = False
arg_num = 0
input_file = "00006_poe2.csv"
output_file = os.path.join(
    # "result-wiki-gw1",
    # "result-wiki-gw2",
    # "result-wiki-poe1",
    "result-wiki-poe2",
    "data",
    "lists",
    "allpages",
    "00006.csv"
)
local_log_file = "pageids-00006_poe2.txt"
outside_log_file = os.path.join(
    # "result-wiki-gw1",
    # "result-wiki-gw2",
    # "result-wiki-poe1",
    "result-wiki-poe2",
    "data",
    "logs",
    "pageids-00006.txt"
)
local_savefiles_file = "savefiles_poe2.txt"
outside_savefiles_file = os.path.join(
    # "result-wiki-gw1",
    # "result-wiki-gw2",
    # "result-wiki-poe1",
    "result-wiki-poe2",
    "data",
    "logs",
    "savefiles.txt"
)

if len(sys.argv) > 1 and sys.argv[1]:
    start = sys.argv[1]
if len(sys.argv) > 2 and sys.argv[2]:
    arg_num = int(sys.argv[2])

append = arg_num * 100 + 2
if start == "yes":
    save_csv(input_file, output_file, append)
    # append_csv(input_file, append)
else:
    append_csv(input_file, output_file, append)
    copy_log(local_log_file, outside_log_file)
    copy_log(local_savefiles_file, outside_savefiles_file)
