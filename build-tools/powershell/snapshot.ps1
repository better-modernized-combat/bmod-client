$date =  Get-Date -Format yyyy-mm-dd-hh-mm-ss

function Export-Backup{
    param(
        $source,
        $destination
    )

Write-Host("Creating a backup of $source")
if (Test-Path($source)){
    Get-ChildItem -Path "$destination" | Where-Object {$_.lastwritetime -le (get-date).adddays(-14)} | ForEach-Object {remove-item $_.fullname -Force -Recurse }
    Get-Childitem -Path "$source" | Copy-item -Destination "$destination\$date" -Force
    }
else{Write-Host("Failed to copy files to $destination")}


7z a $destination/$date.7z $source\*

Remove-Item $destination\$date -Recurse -Force

}

Write-Host Backing up the server database, cleaning up files older than 14 days.
Export-Backup "C:\Users\Administrator\Documents\My Games\Freelancer" "C:\bmod-server\Backups\ServerDB"

Write-Host Backing up the server logs, cleaning up files older than 14 days.
Export-Backup "C:\bmod-server\Freelancer\EXE\logs" "C:\bmod-server\Backups\Logs"

Copy-Item "C:\bmod-server\Freelancer\EXE\flserver.log" -Destination "C:\bmod-server\Backups\Logs\flserver-$date.log"
Copy-Item -Path "C:\bmod-server\Freelancer\EXE\logs" -Destination "C:\bmod-server\Backups\Logs\logs-flhook-$date" -Recurse