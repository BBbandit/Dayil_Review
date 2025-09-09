# 创建Windows计划任务 - 股票数据库自动更新

# 任务配置
$TaskName = "股票数据库自动更新"
$BatchFilePath = "$PSScriptRoot\update_database_advanced.bat"
$WorkingDirectory = "$PSScriptRoot"
$ScheduledTime = "15:30"  # 每天下午3:30执行

# 检查批处理文件是否存在
if (-not (Test-Path $BatchFilePath)) {
    Write-Host "❌ 批处理文件不存在: $BatchFilePath" -ForegroundColor Red
    exit 1
}

# 检查是否已存在同名任务
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "⚠️  计划任务 '$TaskName' 已存在" -ForegroundColor Yellow
    $response = Read-Host "是否删除现有任务并重新创建? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "✅ 已删除现有任务" -ForegroundColor Green
    } else {
        Write-Host "操作取消" -ForegroundColor Yellow
        exit 0
    }
}

# 创建计划任务操作
$action = New-ScheduledTaskAction -Execute $BatchFilePath -WorkingDirectory $WorkingDirectory

# 创建触发器（周一至周五每天下午3:30）
$trigger = New-ScheduledTaskTrigger -Daily -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday -At $ScheduledTime

# 创建任务设置
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 注册计划任务
try {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "自动更新股票数据库数据，每天收盘后执行" -User "SYSTEM" -RunLevel Highest
    
    Write-Host "✅ 计划任务创建成功!" -ForegroundColor Green
    Write-Host "任务名称: $TaskName"
    Write-Host "执行时间: 周一至周五 $ScheduledTime"
    Write-Host "批处理文件: $BatchFilePath"
    Write-Host ""
    Write-Host "可以使用以下命令管理任务:" -ForegroundColor Cyan
    Write-Host "查看任务状态: Get-ScheduledTask -TaskName '$TaskName'"
    Write-Host "立即运行任务: Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host "删除任务: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
    
} catch {
    Write-Host "❌ 创建计划任务失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 测试任务配置
Write-Host ""
Write-Host "测试任务配置..." -ForegroundColor Cyan
$task = Get-ScheduledTask -TaskName $TaskName
if ($task.State -eq 'Ready') {
    Write-Host "✅ 任务配置正常，状态: $($task.State)" -ForegroundColor Green
} else {
    Write-Host "⚠️  任务状态: $($task.State)" -ForegroundColor Yellow
}