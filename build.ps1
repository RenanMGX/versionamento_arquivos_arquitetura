$exclude = @("venv", "botPython.zip", "#material", "Downloads")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "botPython.zip" -Force