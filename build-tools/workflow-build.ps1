Invoke-WebRequest "http://adoxa.altervista.org/freelancer/xml2utf.exe" -OutFile ${github.workspace}\xml2utf.exe
$destination = "${github.workspace}\staging\mod-assets\DATA"
$files = Get-ChildItem -Path "staging\mod-assets\XML" -Filter '*.xml'

foreach($file in $files){
Start-Process -Wait ${github.workspace}\xml2utf.exe -ArgumentList "-o, $destination, $($file.FullName)"
  Write-Host "Compiling $($file.FullName) to UTF"
}
