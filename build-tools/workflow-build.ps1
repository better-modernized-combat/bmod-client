Function Get-TopChildItem($Path, $Filter) {
    $Results = [System.Collections.Generic.List[String]]::New()
    $ProcessingQueue = [System.Collections.Queue]::new()

    ForEach ($item in (Get-ChildItem -Directory $Path)) {
        $ProcessingQueue.Enqueue($item.FullName) 
    }    

    While ($ProcessingQueue.Count -gt 0) {
            $Item = $ProcessingQueue.Dequeue()

            if ($Item -match $Filter) {
                    $Results.Add($Item) 
            }
            else {
                    ForEach ($el in (Get-ChildItem -Path $Item -Directory)) {
                            $ProcessingQueue.Enqueue($el.FullName) 
                    }
            }
    }
    return $Results
}

Invoke-WebRequest "http://adoxa.altervista.org/freelancer/dlt.php?f=xmlproject" -OutFile ${github.workspace}\xmlproject.zip
Expand-Archive ${github.workspace}\xmlproject.zip
$destination = "staging\mod-assets\DATA"
$files = Get-TopChildItem -Path "staging\mod-assets\XML" -Filter '.xml'

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
  Start-Job -ScriptBlock $func -Arg @("staging\xmlproject\XMLUTF.exe", "-o $destination $($file.FullName)")
  Write-Host $destination
  Write-Host $file.FullName
}
