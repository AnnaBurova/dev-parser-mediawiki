import sys
import os

import newtutils.files as NewtFiles

gitignore_file = os.path.join(
    # "result-wiki-gw1",
    "result-wiki-gw2",
    # "result-wiki-poe1",
    # "result-wiki-poe2",
    ".gitignore"
)

csv_file = os.path.join(
    # "result-wiki-gw1",
    "result-wiki-gw2",
    # "result-wiki-poe1",
    # "result-wiki-poe2",
    "data",
    "lists",
    "allpages",
    "006.csv"
)

lines = NewtFiles.read_csv_from_file(csv_file)
assert isinstance(lines, list)

csv_lines = lines[1:]
gitignore_lines = []

for row in csv_lines:
    # if raw_name.startswith("File:"):
    #     raw_name = raw_name[5:]

    file_id = row[0]
    prefix_1 = file_id[:4]
    prefix_2 = file_id[4:7]

    result = f"!data/raw/images/{prefix_1}/{prefix_2}/{file_id}-*"
    gitignore_lines.append(result)

with open(gitignore_file, "a", encoding="utf-8", newline="\n") as f:
    for line in gitignore_lines:
        f.write(line + "\n")

# !data/raw/images/0000/000/0000000011-GuildWarsNightfallLogo.jpg
