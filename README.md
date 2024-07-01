# bmod-client

![Discord](https://img.shields.io/discord/676300713210413087?logo=discord&label=Discord&color=purple)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/better-modernized-combat/bmod-client?label=Issues)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-closed/better-modernized-combat/bmod-client?color=green&label=Issues)
![GitHub Release](https://img.shields.io/github/v/release/better-modernized-combat/bmod-client?label=Release)

Freelancer: Better Modernized Combat (BMOD) is a modification for Freelancer the 2003 space shooter by Digital Anvil. The core goal of the mod is to create a fun and compelling experience for solo and group players in a multiplayer setting. This repository contains the modified client files, as well as the development environment and tools used by the team.

If you just want to download and play the mod, check our the latest release for [the installer](https://github.com/better-modernized-combat/bmod-installer/releases/).

## Setup

- Download and install [Visual Studio Code](https://code.visualstudio.com).
- Download and install the latest version of [Python](https://www.python.org/downloads/).
- Launch VS Code and install the Python Extension from Microsoft.
- Open a terminal window in Visual Studio Code and run `pip install -r requirements.txt`.
- You're ready to go! See below for usage. 

## Usage

- Install Freelancer.
- Copy the installation to a non write-protected location. We recommend `%APPDATA%\freelancer-bmod`.
- Set the system environment variable `FL_PATH` to the `EXE` folder of your copied Freelancer installation.
- Install the [FL Combined Patch](https://cdn.discordapp.com/attachments/661329208609603617/752174852722393169/FLCombinedPatch.exe) over the top of your copied Freelancer installation.

The intended workflow for this script is to have an installation of vanilla Freelancer set up somewhere that this script copies files over to. Using utf.py, the script allows for proper version control and tracking of infocard .dlls and many Freelancer .utf files that are usually compiled binary by compiling them to binary and copying them over at runtime. The script also tails the game's log into the Visual Studio Code console window, and attempts to fetch relevant information when Freelancer.exe crashes unexpectedly.

Once set up in Visual Studio Code, you can start the script by using the 'Start Debugging' option under 'Run' (F5). You can adjust how much the script actually does on run by adding and removing arguments in launch.json. Arguments are as follows:

- `--no_start`: Don't run the game after running the build script section of the script.
- `--no_copy`: Don't copy any files from mod-assets over to the location specified by the `FL_PATH` environment variable.
- `--skip_checks`: Don't validate FL_PATH or check for existing Freelancer processes before proceeding with the copy action. This may cause errors depending on how your environment has been configured.
- `--ignore_xml`: Don't convert any UTF files into XML. If your mod has a lot of UTF files, using this option can save a substantial amount of build time.
- `--ignore_utf`: Don't convert any XML files into UTF. If you're not building UTFs from XML source using this option can save a substantial amount of build time.
- `--ignore_infocards`: Don't build any infocards from infocard_imports.frc. This is unlikely to save much time, but if you're not working with custom strings there isn't much point in using the infocard module.
- `--lua_to_thorn`: Uses Thorn.exe to encode any .lua files as thorn before copying them over to FL_PATH. If you run this with `--no_copy` the files arecan be examined in the `.thorn-cache` folder generated in the root of the repository.
-  `--ini-to-bini`: Uses Bini.exe to encode any .ini files as binary ini before copying them over to FL_PATH. If you run this with `--no_copy` the files arecan be examined in the `.bini-cache` folder generated in the root of the repository.
-  -`--csv_to_ini` Build inis from the specified Google Sheet link defined in `--master_sheet`. You will need to ensure that you're using a valid `service_account.json` file.

Log tailing is set up to work with the default FLSpew.txt location. If your mod moves FLSpew, you'll need to adjust the `flspew_log_path` variable in freelancer.py. Crash handling will attempt to correlate the offset and module from a crash with [the list on the Starport KnowledgeBase](https://the-starport.com/wiki/fl-binaries/crash-offsets), but will fall back to a local file included with this repository if it's unable to reach the remote site.

### Initial Build

- This repository does not contain binary asset files by design, and when you're compiling the client initially for development, you will want to make sure that you don't have the `--ignore_xml` argument enabled. 
- Initial compilation of the client like this will take a few minutes, but once you're set up, running the script with this argument enabled is very quick.

### Pulling Data from Google Sheets

- You'll need to specify your source and destination ini files in `template.json` and `sheet_contents.json` for them to be pulled by the script.
- Source files are a single block type but can be compiled into single files.

### Executable Requirements

Freelancer.exe and some of the plugins we're using require the following redistributibles to run in addition to the Agency FB, Agency FB Bold and Arial Unitype fonts:

- Microsoft Visual C++ 2010 x64 Redistributable
- Microsoft Visual C++ 2013 Redistributable (x64)
- Microsoft Visual C++ 2013 Redistributable (x64)
- Microsoft Visual C++ 2012 Redistributable (x86)
- Microsoft Visual C++ 2015-2022 Redistributable (x86)
- Microsoft Visual C++ 2015-2022 Redistributable (x64)
- Microsoft Visual C++ 2013 Redistributable (x86)
- Microsoft Visual C++ 2012 Redistributable (x64)
- Microsoft Visual C++ 2010 Redistributable (x86)
- Microsoft Visual C++ 2013 Redistributable (x86)

## Credit

- Many thanks to Adoxa and Sir Lancelot for creating the [Freelancer XML Project](http://adoxa.altervista.org/freelancer/tools.html#xmlproject), and [Freelancer Resource Compiler](http://adoxa.altervista.org/freelancer/tools.html#frc), which this set of scripts uses to handle .utf files and infocards respectively, as well as [DeThorn](http://adoxa.altervista.org/freelancer/tools.html#dethorn), the module used to optionally encode .lua scripts to compressed Thorn format and [Bini](http://adoxa.altervista.org/freelancer/tools.html#bini), which encodes ini as binary ini format for fast reading.
- Huge thanks to [Laz](https://github.com/Lazrius) for helping write the original PowerShell scripts this project started as, and also in translating them to Python, and for [FJonske](https://github.com/FJonske) for fine tuning the script and writing the CSV to INI module from scratch.
- Many thanks to [BC46](https://github.com/BC46) for allowing us to use the excellent texture and model improvements from Freelancer: HD Edition.
- Thanks once again to Adoxa for the use of his many plugins, which are in use throughout this project.
- Thank you to Why485 for the use of his excellent Big Huge Effects Pack.
