# $i = 12
for ($i = 12; $i -le 17; $i++) {


  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/run_poe1.py "yes" $i 2>&1


  # @(
  #   "3"
  #   "2"
  #   "6"
  # ) | & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py 2>&1

  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py guild_wars_1.json 2 6 2>&1
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py guild_wars_2.json 2 6 2>&1
  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py path_of_exile_1.json 2 6 2>&1
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py path_of_exile_2.json 2 6 2>&1


  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/names_to_gitignore_poe1.py 2>&1


  # @(
  #   "3"
  #   "5"
  # ) | & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py 2>&1

  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py guild_wars_1.json 5 2>&1
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py guild_wars_2.json 5 2>&1
  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py path_of_exile_1.json 5 2>&1
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py path_of_exile_2.json 5 2>&1


  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/run_poe1.py "no" $i 2>&1


  "13" | & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-tools/tools/git/commit.py 2>&1


  # "13" | & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-tools/tools/git/edit_last_date.py 2>&1


}

# powershell -ExecutionPolicy Bypass -File run_sequence_poe1.ps1 2>&1
