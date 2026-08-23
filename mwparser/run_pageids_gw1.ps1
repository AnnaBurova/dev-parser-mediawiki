$pythonExe = "D:/VS_Code/.venv314/Scripts/python.exe"
$scriptPath = "D:/VS_Code/dev-parser-mediawiki/mwparser/script.py"

$numbers_gw1 = @(
    # "006",
    "000", "001", "002", "003", "004", "005", "007",
    "008", "009", "010", "011", "012", "013", "014", "015",
    "100", "101", "102", "103", "200", "201", "202", "203",
    "274", "275"
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

Invoke-WikiRun -WikiName "gw1"  -WikiMenuNumber "1" -Numbers $numbers_gw1

# . 'D:\VS_Code\dev-parser-mediawiki\mwparser\run_pageids_gw1.ps1'
