$pythonExe = "D:/VS_Code/.venv314/Scripts/python.exe"
$scriptPath = "D:/VS_Code/dev-parser-mediawiki/mwparser/script.py"

$numbers_gw2 = @(
    "006",
    "000", "001", "002", "003", "004", "005", "007",
    "008", "009", "010", "011", "012", "013", "014", "015",
    "102", "103", "106", "107", "108", "109", "112", "113",
    "114", "115", "200", "201", "202", "203", "274", "275"
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

        $logPath = "$repoPath\data\logs\pageids-$number.txt"

        if (Test-Path $logPath) {
            Remove-Item $logPath
        }

        @(
            $WikiMenuNumber
            "2"
            [int]$number
        ) | & $pythonExe $scriptPath
    }
}

Invoke-WikiRun -WikiName "gw2"  -WikiMenuNumber "2" -Numbers $numbers_gw2

# . 'D:\VS_Code\dev-parser-mediawiki\mwparser\run_pageids_gw2.ps1'
