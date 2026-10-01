$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$tools = Join-Path $root "tools"
$jarUrl = "https://repo1.maven.org/maven2/io/zonky/test/postgres/embedded-postgres-binaries-windows-amd64/16.9.0/embedded-postgres-binaries-windows-amd64-16.9.0.jar"
$jarPath = Join-Path $tools "pg.jar"
$zipDir = Join-Path $tools "pgzip"
$pgHome = Join-Path $tools "pgsql"
$dataDir = Join-Path $tools "pgdata"

Write-Host "Downloading PostgreSQL binaries..."
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $jarUrl -OutFile $jarPath -UseBasicParsing
Write-Host "Download complete."

if (Test-Path $zipDir) { Remove-Item -Recurse -Force $zipDir }
New-Item -ItemType Directory -Force -Path $zipDir | Out-Null
Expand-Archive -Path $jarPath -DestinationPath $zipDir -Force
$txz = Get-ChildItem $zipDir -Filter "*.txz" | Select-Object -First 1
if (-not $txz) { throw "No .txz found inside jar" }

if (Test-Path $pgHome) { Remove-Item -Recurse -Force $pgHome }
New-Item -ItemType Directory -Force -Path $pgHome | Out-Null
tar -xf $txz.FullName -C $pgHome
Write-Host "Extraction complete: $pgHome"

$postgresBin = Join-Path $pgHome "bin\postgres.exe"
if (-not (Test-Path $postgresBin)) { throw "postgres.exe not found" }

if (-not (Test-Path $dataDir)) {
    $pwFile = Join-Path $tools "pwfile.txt"
    Set-Content -Path $pwFile -Value "postgres" -NoNewline
    & (Join-Path $pgHome "bin\initdb.exe") -D $dataDir -U postgres --pwfile=$pwFile -A password -E UTF8 --locale=C
    Remove-Item -Force $pwFile
    Write-Host "initdb complete."
}

& (Join-Path $pgHome "bin\pg_ctl.exe") -D $dataDir -o "-p 5432" -l (Join-Path $tools "pg.log") start
Start-Sleep -Seconds 3
& (Join-Path $pgHome "bin\createdb.exe") -U postgres -h localhost -p 5432 timetable_db
& (Join-Path $pgHome "bin\psql.exe") -U postgres -h localhost -p 5432 -d timetable_db -c "SELECT version();"
Write-Host "PostgreSQL ready on port 5432, database timetable_db created."
