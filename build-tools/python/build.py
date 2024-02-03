import argparse
import time

from bini import *
from checks import *
from copy_assets import *
from crc import *
from freelancer import *
from generate_inis import generate_inis
from infocards import *
from thorn import *
from utf import *
from utils import *

parser = argparse.ArgumentParser()
parser.add_argument("--no_start", help="Runs the script but does not start Freelancer.exe on finish.", action="store_true")
parser.add_argument("--no_copy", help="Runs the script but does not copy files.", action="store_true")
parser.add_argument("--skip_checks", help="Skips validation and checking stages.", action="store_true")
parser.add_argument("--ignore_xml", help="Skips the conversion of XML into UTF.", action="store_true")
parser.add_argument("--ignore_utf", help="Skips the conversion of UTF into XML.", action="store_true")
parser.add_argument("--ignore_infocards", help="Skips the compiling of infocards from infocard_imports.frc", action="store_true")
parser.add_argument("--lua_to_thorn", help="Encodes lua to thorn format before copying.", action="store_true")
parser.add_argument("--ini_to_bini", help="Encodes ini to bini format before copying.", action="store_true")
parser.add_argument("--csv_to_ini", help="Build selected INI files from CSV.", action="store_true")
parser.add_argument("--master_sheet", help="This is the master sheet INI files will be generated from. Accepts both a URL or a file path from your machine.")
parser.add_argument("--ignore_weapon_balance", help="If True, disables the sanity checker when building weapons", action="store_true", default=False)
parser.add_argument("--no_crc", help="Prevents the script generating a hashmap after copying files.")

args = parser.parse_args()

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print(bcolors.HEADER + f"Starting build and copy script at {current_time}" + bcolors.ENDC)
build_script_start_time = time.perf_counter() 

if not args.skip_checks:
    validate_path()
else:
    print(bcolors.WARNING + "Warning, checks have been disabled. You may experience errors if the the FL_PATH environment variable has not been set" + bcolors.ENDC)

if not args.ignore_infocards:
    compile_infocards()
    compile_infocards2()

if args.csv_to_ini:
    generate_inis(master_sheet = args.master_sheet, weapon_sanity_check = (not args.ignore_weapon_balance))

if not args.ignore_utf:
    utf_xml_start_time = time.perf_counter() 
    print(f"Converting UTF files at '{utf_path}' to XML format...")
    utf_to_xml_thread()
    utf_xml_end_time = time.perf_counter() 
    print(f"Converted UTF files at '{utf_path}' to XML in {utf_xml_end_time - utf_xml_start_time:0.4f} seconds")

if not args.ignore_xml:
    xml_utf_start_time = time.perf_counter() 
    print(f"Converting XML files at '{xml_path}' to UTF format...")                         
    xml_to_utf_thread()
    xml_utf_end_time = time.perf_counter() 
    print(f"Converted XML files at '{xml_path}' to UTF in {xml_utf_end_time - xml_utf_start_time:0.4f} seconds")

if not args.skip_checks:
    validate_process_stopped()
else:
    print(bcolors.WARNING + "Warning, checks have been disabled. You may experience copy errors if any instances of Freelancer are still running" + bcolors.ENDC)

if args.lua_to_thorn:
    lua_thorn_start_time = time.perf_counter() 
    print(f"Encoding LUA files to Thorn from '{lua_path}'...")  
    lua_to_thorn_thread()
    lua_thorn_end_time = time.perf_counter() 
    print(f"LUA files encoded to Thorn in {lua_thorn_end_time - lua_thorn_start_time:0.4f} seconds")

if not args.no_copy:
    copy_files()
if not args.no_crc:    
    generate_hashes()

if args.lua_to_thorn and not args.no_copy:
    copy_thorn_cleanup_cache()

if args.ini_to_bini:
    ini_bini_start_time = time.perf_counter() 
    print(f"Encoding INI files to BINI from '{ini_path}'...")  
    ini_to_bini_thread()
    ini_bini_end_time = time.perf_counter() 
    print(f"INI files encoded to BINI in {ini_bini_end_time - ini_bini_start_time:0.4f} seconds")

if args.ini_to_bini and not args.no_copy:
    copy_bini_cleanup_cache()

build_script_end_time = time.perf_counter() 
print(bcolors.HEADER + f"Build script completed in {build_script_end_time - build_script_start_time:0.4f} seconds" + bcolors.ENDC)

if not args.no_start:
    start_freelancer_main()