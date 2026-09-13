# playwright-cli 批处理驱动器
# 用途：在【同一次 PowerShell 调用内】完成一整段浏览器会话（沙箱会在调用结束后回收进程树，
#       因此浏览器无法跨调用存活）。登录态通过 state-save / state-load 落盘复用到下一次调用。
#
# 用法： pwrun.ps1 -CommandFile <命令文件> [-LogFile <日志文件>]
# 命令文件格式：每行一条指令，用 | 分隔参数；支持伪指令 sleep|<毫秒>
#   例： open|http://127.0.0.1/admin/login
#        fill|e19|13800000000
#        click|e32
#        sleep|1500
#        snapshot|p1-login.yaml

param(
    [Parameter(Mandatory = $true)][string]$CommandFile,
    [string]$LogFile = "$env:TEMP\pwrun.log"
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$node = "C:\Users\Administrator\.workbuddy\binaries\node\versions\22.22.2-3\node.exe"
$pcliJs = "C:\Users\Administrator\.workbuddy\binaries\node\workspace\node_modules\@playwright\cli\playwright-cli.js"

Set-Location "D:\project\tiku\tiku"

"" | Out-File $LogFile -Encoding utf8

if (-not (Test-Path $CommandFile)) {
    "ERROR: 命令文件不存在 $CommandFile" | Out-File $LogFile -Append -Encoding utf8
    exit 1
}

# 显式以 UTF-8 + .NET 读取并按行拆分（Get-Content 在本机对 LF 文件的拆行行为不可靠）
$text = [System.IO.File]::ReadAllText($CommandFile, [System.Text.Encoding]::UTF8)
$all = $text -split "\r?\n"
$lines = $all | Where-Object { $_.Trim() -ne "" -and -not $_.Trim().StartsWith("#") }

"DEBUG cmdFile=[$CommandFile] exists=$(Test-Path $CommandFile)" | Out-File $LogFile -Append -Encoding utf8
"DEBUG textLen=$($text.Length) all=$(@($all).Count) lines=$(@($lines).Count)" | Out-File $LogFile -Append -Encoding utf8
"DEBUG head=$($text.Substring(0, [Math]::Min(80, $text.Length)))" | Out-File $LogFile -Append -Encoding utf8

$idx = 0
foreach ($line in $lines) {
    $idx++
    $parts = $line.Trim() -split '\|'
    $cmd = $parts[0].Trim()

    if ($cmd -eq "sleep") {
        $ms = [int]$parts[1].Trim()
        "----- [$idx] sleep $ms ms" | Out-File $LogFile -Append -Encoding utf8
        Start-Sleep -Milliseconds $ms
        continue
    }

    $argv = @()
    for ($i = 0; $i -lt $parts.Count; $i++) { $argv += $parts[$i].Trim() }

    "===== [$idx] $($argv -join ' ')" | Out-File $LogFile -Append -Encoding utf8
    try {
        # 直接调用 node 执行 CLI 入口，绕开 cmd.exe 包装层，避免中文参数被控制台代码页破坏
        $res = & $node $pcliJs @argv 2>&1 | Out-String
        $res.Trim() | Out-File $LogFile -Append -Encoding utf8
    } catch {
        "EXCEPTION: $($_.Exception.Message)" | Out-File $LogFile -Append -Encoding utf8
    }
    Start-Sleep -Milliseconds 600
}

"===== DONE ($idx commands)" | Out-File $LogFile -Append -Encoding utf8
Write-Output "done: $idx"
