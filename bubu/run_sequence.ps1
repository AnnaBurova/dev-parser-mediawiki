# $i = 12
for ($i = 167; $i -le 176; $i++) {

  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/run.py "yes" 3
  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/run.py "yes" $i


  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py guild_wars_1.json 2 6
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py guild_wars_2.json 2 6
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py path_of_exile_1.json 2 6
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py path_of_exile_2.json 2 6


  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/names_to_gitignore.py


  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py guild_wars_1.json 5
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py guild_wars_2.json 5
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py path_of_exile_1.json 5
  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-parser-mediawiki/mwparser/script.py path_of_exile_2.json 5


  # & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/run.py "no" 7
  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/run.py "no" $i


  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-tools/tools/git/commit.py


  & d:/VS_Code/.venv314/Scripts/python.exe d:/VS_Code/dev-tools/tools/git/edit_last_date.py

}

# powershell -ExecutionPolicy Bypass -File run_sequence.ps1
