
Invoke-Item (Start-Process powershell ((Split-Path $MyInvocation.InvocationName) + "\snapshot.ps1"))
Remove-Item "C:\bmod-server\Freelancer\EXE\logs" -Recurse -Force
