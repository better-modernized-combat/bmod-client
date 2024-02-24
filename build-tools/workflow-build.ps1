Invoke-WebRequest "http://adoxa.altervista.org/freelancer/dlt.php?f=xmlproject" -OutFile ${github.workspace}\xmlproject.zip
Expand-Archive ${github.workspace}\xmlproject.zip
$destination = "${github.workspace}\staging\mod-assets\DATA"
$files = Get-ChildItem -Path "staging\mod-assets\XML" -Filter '*.xml'

$func = {
param(     
    [Parameter(Mandatory)]   
    [string]$proc,
    [Parameter(Mandatory)]
    [string]$params
)
Start-Process -FilePath "$proc" -Wait -ArgumentList $params
}

foreach($file in $files){
Start-Process -FilePath "${github.workspace}\xmlproject\XMLUTF.exe", -ArgumentList "-o", "$destination", "$($file.FullName)"
  Write-Host $destination
  Write-Host $file.FullName
  Write-Host $func
}
