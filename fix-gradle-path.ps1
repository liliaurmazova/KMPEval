# Fix Gradle PATH for current PowerShell session
# Run this script if you get "gradle is not recognized" error

Write-Host "🔧 Fixing Gradle PATH..." -ForegroundColor Yellow

# Check if Gradle is in the correct location
$gradleBinPath = "C:\Gradle\bin"
if (Test-Path "$gradleBinPath\gradle.bat") {
    Write-Host "✅ Found Gradle at: $gradleBinPath" -ForegroundColor Green
    
    # Update PATH for current session
    $newPath = ($env:PATH -replace 'C:\\Gradle\\gradle-9\.1\.0\\bin', 'C:\Gradle\bin')
    $env:PATH = $newPath
    
    Write-Host "✅ PATH updated for current session" -ForegroundColor Green
    
    # Test gradle command
    try {
        $gradleVersion = gradle -v 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Gradle is now working!" -ForegroundColor Green
            gradle -v | Select-String "Gradle"
        } else {
            Write-Host "❌ Gradle command still not working" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error testing gradle command: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Gradle not found at expected location: $gradleBinPath" -ForegroundColor Red
    Write-Host "   Please check your Gradle installation" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "💡 To fix PATH permanently:" -ForegroundColor Cyan
Write-Host "   1. Run PowerShell as Administrator" -ForegroundColor White
Write-Host "   2. Execute this script again with admin rights" -ForegroundColor White
Write-Host "   OR" -ForegroundColor White
Write-Host "   3. Manually update System Environment Variables:" -ForegroundColor White
Write-Host "      Change 'C:\Gradle\gradle-9.1.0\bin' to 'C:\Gradle\bin'" -ForegroundColor White