$exclude = @("venv", "botPython.zip", "#material", "Downloads", "Logs")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "botPython.zip" -Force