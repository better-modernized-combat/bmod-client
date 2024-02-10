# Compiles infocards from the .frc file located at frc_input_path and creates a DLL at frc_output_path.
import subprocess
import time

from utils import root_copy_path
from utils import bcolors

frc_input_path = f"{root_copy_path}\\mod-assets\\infocard_imports.frc"
frc_output_path = f"{root_copy_path}\\mod-assets\\EXE\\BmodInfocards.dll"

frc2_input_path = f"{root_copy_path}\\mod-assets\\weapon_infocard_imports.frc"
frc2_output_path = f"{root_copy_path}\\mod-assets\\EXE\\BmodWeaponInfocards.dll"

def compile_infocards():
    print(bcolors.OKBLUE + "Compiling infocards from {} to {}...".format(frc_input_path, frc_output_path) + bcolors.ENDC)
    infocard_start_time = time.perf_counter() 
    return_code = subprocess.call([f"{root_copy_path}\\build-tools\\frc.exe", f"{frc_input_path}", f"{frc_output_path}"])
    if return_code != 0:
        print(bcolors.FAIL + f"Freelancer Resource Compiler has failed to compile the infocard .dll file. Please check your Windows Event logs" + bcolors.ENDC)
    else:
        infocard_end_time = time.perf_counter() 
        print(bcolors.OKGREEN + f"Infocards compiled in {infocard_end_time - infocard_start_time:0.4f} seconds" + bcolors.ENDC)

# TODO: Swap this over so the function can take args and call it twice instead. 
def compile_infocards2():
    print(bcolors.OKBLUE + "Compiling infocards from {} to {}...".format(frc_input_path, frc_output_path) + bcolors.ENDC)
    infocard_start_time = time.perf_counter() 
    return_code = subprocess.call([f"{root_copy_path}\\build-tools\\frc.exe", f"{frc2_input_path}", f"{frc2_output_path}"])
    if return_code != 0:
        print(bcolors.FAIL + f"Freelancer Resource Compiler has failed to compile the infocard .dll file. Please check your Windows Event logs" + bcolors.ENDC)
    else:
        infocard_end_time = time.perf_counter() 
        print(bcolors.OKGREEN + f"Infocards compiled in {infocard_end_time - infocard_start_time:0.4f} seconds" + bcolors.ENDC)