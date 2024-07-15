function Get-LatestRelease{
    param(
        $repo,
        $file,
        $ext,
        $dest
    )

    $releases = "https://api.github.com/repos/$repo/releases"

    Write-Host Determining latest release
    $tag = (Invoke-WebRequest $releases | ConvertFrom-Json)[0].tag_name
    
    $download = "https://github.com/$repo/releases/download/$tag/$file"
    $name = $file.Split(".")[0]
    
    try{
    New-Item -Path "C:\bmod-server\staging\" -Name "$name-$tag" -ItemType "directory"
    }
    catch [System.Net.WebException],[System.IO.IOException] {
        "The path 'C:\bmod-server\staging\$name-$tag' already exists"
    }
    
    $zip = "C:\bmod-server\staging\$name-$tag\$name.$ext"
    
    Write-Host Dowloading latest release from $download
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest $download -Out $zip
    $ProgressPreference = 'Continue'
    
    Write-Host Extracting release files
    7z x $zip -y -oC:\bmod-server\staging\$name-$tag\unpacked
    
    Write-Host Installing latest release
    Copy-Item -Path "C:\bmod-server\staging\$name-$tag\unpacked\*" -Destination $dest -Recurse -Force
    

}

Get-LatestRelease "better-modernized-combat/bmod-client" "Release.7z" "7z" "C:\bmod-server\Freelancer"

#Cutting the latest release of FLHook right now as the auto-build isn't running on the box.

#Get-LatestRelease "TheStarport/FLHook" "Release.zip" "zip" "C:\bmod-server\staging"

#Write-Host Installing the latest release of FLHook
#Copy-Item -Path "C:\bmod-server\staging\Release\*" -Destination "C:\bmod-server\Freelancer\EXE" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\advanced_startup_solars.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\autobuy.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\bountyhunt.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\cash_manager.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\ip_ban.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\mark.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\message.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\misc_commands.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\npc.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\rename.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\stats.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\solar.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force
#Copy-Item -Path "C:\bmod-server\staging\Release\plugins\loottables.dll" -Destination "C:\bmod-server\Freelancer\EXE\plugins" -Force

Write-Host Updating FLHook configuration files
Set-Location "C:\Users\Administrator\Documents\GitHub\bmod-flhook-configs"
git checkout main
git pull

Write-Host Installing latest FLHook configuration files
Copy-Item "C:\Users\Administrator\Documents\GitHub\bmod-flhook-configs\FLHook.json" -Destination "C:\bmod-server\Freelancer\EXE\FLHook.json" -Force
Copy-Item "C:\Users\Administrator\Documents\GitHub\bmod-flhook-configs\config\*" -Destination "C:\bmod-server\Freelancer\EXE\config" -Recurse -Force

Write-Host Cleaning up
Remove-Item "C:\bmod-server\staging" -Recurse -Force
