# $i = 14
for ($i = 15; $i -le 20; $i++) {


  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/run_gw2.py "yes" $i 2>&1


  # @(
  #   "2"
  #   "2"
  #   "6"
  # ) | & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py 2>&1

  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py guild_wars_1.json 2 6 2>&1
  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py guild_wars_2.json 2 6 2>&1
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py path_of_exile_1.json 2 6 2>&1
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py path_of_exile_2.json 2 6 2>&1


  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/names_to_gitignore_gw2.py 2>&1


  # @(
  #   "2"
  #   "5"
  # ) | & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py 2>&1

  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py guild_wars_1.json 5 2>&1
  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py guild_wars_2.json 5 2>&1
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py path_of_exile_1.json 5 2>&1
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py path_of_exile_2.json 5 2>&1


  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/run_gw2.py "no" $i 2>&1


  "12" | & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-tools/tools/git/commit.py 2>&1


  # "12" | & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-tools/tools/git/edit_last_date.py 2>&1


}

# powershell -ExecutionPolicy Bypass -File run_sequence_gw2.ps1 2>&1
