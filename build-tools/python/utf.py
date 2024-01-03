# Decompiles UTF files to XML and then back again for version control.
import glob
import os
import subprocess

from utils import *

utf_types = (".3db", ".ale", ".cmp", ".mat", ".sph", ".txm", ".utf", ".vms")
utf_path = f"{root_copy_path}\\mod-assets\\DATA\\"
xml_path = f"{root_copy_path}\\mod-assets\\XML\\"
    
from concurrent.futures import ThreadPoolExecutor

# UTFXML.exe creates a 'path' key in the root node of anything it decompiles equal to utf_path + any subfolders. This path is used to recompile the .xml file into .utf when XMLUTF.exe is called. If you're importing .xml files to convert. .utf, make sure this key is set correctly.
def convert_file_utf_xml(input_file, output_file):
    return_code = subprocess.Popen(["build-tools\\UTFXML.exe",
                      "-agi", "-o", output_file, input_file]).wait()
    if return_code !=0:
        print(bcolors.FAIL + f"Failed to convert {input_file}" + bcolors.ENDC)

def utf_to_xml_thread():
    executor = ThreadPoolExecutor(max_workers = 128)

    for file in glob.glob(f"{utf_path}\\**\\*", recursive=True):
        if file.endswith(utf_types):
            filename = os.path.basename(file)
            executor.submit(convert_file_utf_xml, file, xml_path)

    executor.shutdown()

def convert_file_xml_utf(input_file, output_file):
    return_code = subprocess.Popen(["build-tools\\XMLUTF.exe",
                      "-o", output_file, input_file]).wait()
    if return_code !=0:
        print(bcolors.FAIL + f"Failed to convert {input_file}" + bcolors.ENDC)

def xml_to_utf_thread():
    executor = ThreadPoolExecutor(max_workers = 128)

    for file in glob.glob(f"{xml_path}\\**\\*.xml", recursive=True):
        filename = os.path.basename(file)
        if (filename.endswith(".vms.xml") and filename != "interface.generic.vms.xml") or filename.endswith("vwd.xml") or filename =="Animation.xml":
            continue
        output_path = file.replace(xml_path, utf_path).replace(filename, "")
        executor.submit(convert_file_xml_utf, file, output_path)

    executor.shutdown()