# 第51作「32キロの初出勤」を、画像44場面つきの動画に書き出す（Windows / PowerShell）
#
# 使い方（MP3 と SRT のパスを渡す。日本語・空白を含んでも "" で囲めばOK）:
#   powershell -ExecutionPolicy Bypass -File tools\build_ep51_windows.ps1 `
#       -Mp3 "C:\...\xxx.mp3" -Srt "C:\...\xxx.srt" -Out "D:\codex kandou-move\outputs" [-Mode final|preview]
#
# 初回は my-project を取得し、Pillow を入れ、画像44枚とフォントを取得する。2回目以降は取得済みを飛ばす。
# 書き出し途中で止まっても、同じコマンドで続きから再開できる。
# 注意: このファイルは文字化け防止のため ASCII のみで書いてある。

param(
    [Parameter(Mandatory = $true)][string]$Mp3,
    [Parameter(Mandatory = $true)][string]$Srt,
    [string]$Out = "$HOME\Downloads",
    [ValidateSet("final", "preview")][string]$Mode = "final",
    [string]$Work = "$HOME\Downloads\my-project"
)
$ErrorActionPreference = "Stop"

function Need($cmd, $hint) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "$cmd not found. $hint" }
}
Need git "Install Git for Windows."
Need python "Install Python."
Need ffmpeg "winget install --id Gyan.FFmpeg -e  (then reopen PowerShell)"

foreach ($p in @($Mp3, $Srt)) { if (-not (Test-Path -LiteralPath $p)) { throw "File not found: $p" } }

if (-not (Test-Path "$Work\.git")) {
    git clone --depth 1 --branch claude/inspiring-pasteur-vnfp2f https://github.com/kokeko2ko-ui/my-project $Work
}
python -m pip install --quiet pillow

$unit = "$Work\video\51_walk"
New-Item -ItemType Directory -Force "$unit\source" | Out-Null
# unit.json: UTF-8 without BOM, ASCII title
[IO.File]::WriteAllText("$unit\unit.json", '{"title": "ep51_32km"}', (New-Object Text.UTF8Encoding($false)))
Copy-Item -LiteralPath $Mp3 "$unit\source\narration.mp3" -Force
Copy-Item -LiteralPath $Srt "$unit\source\narration.srt" -Force

Push-Location $Work
try {
    python -I tools\video\setup.py video\51_walk
    python -I tools\video\build.py video\51_walk check
    Write-Host "`nIf the check above looks right, rendering starts (this takes a while)..."
    python -I tools\video\build.py video\51_walk $Mode
    New-Item -ItemType Directory -Force $Out | Out-Null
    Copy-Item -LiteralPath "$unit\build\ep51_32km_$Mode.mp4" $Out -Force
    Write-Host "`nDONE: $Out\ep51_32km_$Mode.mp4"
}
finally { Pop-Location }
