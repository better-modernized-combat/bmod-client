

$destination = "$PSScriptRoot\staging\mod-assets\DATA"
$files = Get-ChildItem "$PSScriptRoot\staging\mod-assets\XML" -exclude *.vms.xml*, *vwd.xml*, *Animation.xml*, 

$counter = [pscustomobject] @{ Value = 0 }
$groupSize = 100

$groups = $files | Group-Object -Property { [math]::Floor($counter.Value++ / $groupSize) }
    
foreach ($group in $groups) {
    $jobs = foreach ($file in $group.Group) {
        Start-Job -ScriptBlock $func -Arg @("$PSScriptRoot\xmlproject\XMLUTF.exe", "-o $destination $($file.FullName)")
        Write-Host "Converting $($file) and writing it to $destination"
    }
    Receive-Job $jobs -Wait -AutoRemoveJob
}
