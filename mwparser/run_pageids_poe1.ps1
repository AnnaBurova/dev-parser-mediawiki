$pythonExe = "D:/VS_Code/.venv314/Scripts/python.exe"
$scriptPath = "D:/VS_Code/dev-parser-mediawiki/mwparser/script.py"

$numbers_poe1 = @(
    "00006",
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

Invoke-WikiRun -WikiName "poe1" -WikiMenuNumber "3" -Numbers $numbers_poe1

# . 'D:\VS_Code\dev-parser-mediawiki\mwparser\run_pageids_poe1.ps1'
