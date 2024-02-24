$func = {
    param(     
        [Parameter(Mandatory)]   
        [string]$proc,
        [Parameter(Mandatory)]
        [string]$params
    )
    Start-Process -FilePath "$proc" -Wait -ArgumentList $params
}

$destination = "staging\mod-assets\DATA"
$files = Get-ChildItem "staging\mod-assets\XML"

$counter = [pscustomobject] @{ Value = 0 }
$groupSize = 100

$groups = $files | Group-Object -Property { [math]::Floor($counter.Value++ / $groupSize) }
    
foreach ($group in $groups) {
    $jobs = foreach ($file in $group.Group) {
        Start-Job -ScriptBlock $func -Arg @("staging\xmlproject\XMLUTF.exe", "-o $destination $($file.FullName)")
        Write-Host "Converting $($file) and writing it to $destination $($file.FullName)"
    }
    Receive-Job $jobs -Wait -AutoRemoveJob
}
