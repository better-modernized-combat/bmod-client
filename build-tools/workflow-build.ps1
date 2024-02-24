Invoke-WebRequest "http://adoxa.altervista.org/freelancer/dlt.php?f=xmlproject" -OutFile ${github.workspace}\xmlproject.zip
Expand-Archive ${github.workspace}\xmlproject.zip
$destination = "${github.workspace}\staging\mod-assets\DATA"
$files = Get-ChildItem "staging\mod-assets\XML"

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
  Start-Job -ScriptBlock $func -Arg @("${github.workspace}\staging\xmlproject\XMLUTF.exe", "-o $destination $($file.FullName)")
}
