Invoke-WebRequest "http://adoxa.altervista.org/freelancer/xml2utf.exe" -OutFile ${github.workspace}\xml2utf.exe
$files = Get-ChildItem -Path "staging\mod-assets\XML" -Filter '*.xml'
Set-Location "${github.workspace}/staging"
foreach($file in $files){
Start-Process -Wait ${github.workspace}\xml2utf.exe -ArgumentList "-o ${github.workspace}/staging/mod-assets/DATA $($file.FullName)"
  Write-Host "Compiling $($file.FullName) to UTF"
}