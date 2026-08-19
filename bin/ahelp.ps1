param(
    [Parameter(Position=0, Mandatory=$true)][string]$Query,
    [switch]$Search,
    [switch]$Latest,
    [switch]$Offline,
    [int]$Limit = 20,
    [string]$ArturoBin = $(if ($env:ARTURO_BIN) { $env:ARTURO_BIN } else { "arturo" })
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Index = Join-Path $Root "references/library-index.csv"
$Aliases = @{
    "++"="append"; "--"="remove"; "+"="add"; "-"="sub"; "*"="mul";
    "/"="div"; "//"="fdiv"; "%"="mod"; "^"="pow"; "="="equal?";
    "<"="less?"; ">"="greater?"; "=<"="lessOrEqual?"; ">="="greaterOrEqual?";
    "<>"="notEqual?"; ".."="range"; "@"="array"; "#"="dictionary";
    '$'="function"; "~"="render"; "<<"="read"; ">>"="write"; "??"="coalesce"
}
$Lookup = if ($Aliases.ContainsKey($Query)) { $Aliases[$Query] } else { $Query }

if (-not $Offline) {
    $cmd = Get-Command $ArturoBin -ErrorAction SilentlyContinue
    if ($cmd -and $Query -match '^[A-Za-z0-9_?+*/%<>=!~|@#$^.-]+$') {
        Write-Output "--- Arturo runtime: info '$Query ---"
        & $ArturoBin --no-color -e "info '$Query"
        Write-Output "--- Official documentation index ---"
    } else {
        Write-Warning "Arturo runtime not found or query is not a single safe symbol; using offline index."
    }
}

$rows = Import-Csv $Index
if ($Search) {
    $found = $rows | Where-Object { $_.name -like "*$Lookup*" -or $_.module -like "*$Lookup*" } | Select-Object -First $Limit
} else {
    $found = $rows | Where-Object { $_.name -ieq $Lookup } | Select-Object -First $Limit
}
if (-not $found) { throw "No indexed match for '$Query'. Try -Search." }
foreach ($r in $found) {
    if ($Latest -and $r.latest_http_status -eq "200") { $url = $r.latest_url; $note = "" }
    elseif ($Latest) { $url = $r.stable_url; $note = " [latest=$($r.latest_http_status); stable fallback]" }
    else { $url = $r.stable_url; $note = "" }
    Write-Output "$($r.name)`t$($r.module)`t$url$note"
}
