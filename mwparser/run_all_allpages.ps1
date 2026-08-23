$pythonExe = "D:/VS_Code/.venv314/Scripts/python.exe"
$scriptPath = "D:/VS_Code/dev-parser-mediawiki/mwparser/script.py"

$numbers_gw1 = @(
    # "006",
    "000", "001", "002", "003", "004", "005", "007",
    "008", "009", "010", "011", "012", "013", "014", "015",
    "100", "101", "102", "103", "200", "201", "202", "203",
    "274", "275"
)

$numbers_gw2 = @(
    # "006",
    "000", "001", "002", "003", "004", "005", "007",
    "008", "009", "010", "011", "012", "013", "014", "015",
    "102", "103", "106", "107", "108", "109", "112", "113",
    "114", "115", "200", "201", "202", "203", "274", "275"
)

$numbers_poe1 = @(
    # "00006",
    "00000", "00001", "00002", "00003", "00004", "00005", "00007",
    "00008", "00009", "00010", "00011", "00012", "00013", "00014", "00015",
    "00274", "00275", "00828", "00829", "02300", "02301", "02302", "02303",
    "10000", "10001", "10002", "10003", "10004", "10005", "10006", "10007",
    "10008", "10009", "10010", "10011", "10012", "10013", "10014", "10015",
    "10016", "10017"
)

$numbers_poe2 = @(
    # "00006",
    "00000", "00001", "00002", "00003", "00004", "00005", "00007",
    "00008", "00009", "00010", "00011", "00012", "00013", "00014", "00015",
    "00274", "00275", "00828", "00829", "02300", "02301", "02302", "02303",
    "10000", "10001", "10002", "10003", "10004", "10005", "10006", "10007",
    "10008", "10009", "10010", "10011", "10012", "10013", "10014", "10015",
    "10016", "10017"
)

function Invoke-WikiRun {
    param (
        [string]$WikiName,
        [string]$WikiMenuNumber,
        [string[]]$Numbers
    )

    $repoPath = "D:\VS_Code\result-wiki-$WikiName"

    foreach ($number in $Numbers) {
        Write-Host "Run $WikiName for number: $number"

        $csvPath = "$repoPath\data\lists\allpages\$number.csv"
        $logPath = "$repoPath\data\logs\allpages-$number.txt"

        if (Test-Path $csvPath) {
            Remove-Item $csvPath
        }

        if (Test-Path $logPath) {
            Remove-Item $logPath
        }

        @(
            $WikiMenuNumber
            "1"
            [int]$number
        ) | & $pythonExe $scriptPath
    }
}

# Invoke-WikiRun -WikiName "gw1"  -WikiMenuNumber "1" -Numbers $numbers_gw1
# Invoke-WikiRun -WikiName "gw2"  -WikiMenuNumber "2" -Numbers $numbers_gw2
# Invoke-WikiRun -WikiName "poe1" -WikiMenuNumber "3" -Numbers $numbers_poe1
Invoke-WikiRun -WikiName "poe2" -WikiMenuNumber "4" -Numbers $numbers_poe2

# . 'D:\VS_Code\dev-parser-mediawiki\mwparser\run_all_allpages.ps1'
