import glob
import subprocess
import shutil

from concurrent.futures import ThreadPoolExecutor

from utils import *

ini_path = f"{root_copy_path}\\mod-assets\\DATA\\"
bini_cache = f"{root_copy_path}\\.bini-cache\\"

def convert_file_ini_bini(input_file, output_file):
    shutil.copyfile(input_file, output_file)
    return_code = subprocess.Popen(["build-tools\\bini.exe","-o", output_file]).wait()
    if return_code != 0:
        print(bcolors.FAIL + f"Failed to convert {input_file}" + bcolors.ENDC)
def ini_to_bini_thread():
    cache_exists = os.path.isdir(bini_cache)
    if cache_exists == True:
         shutil.rmtree(bini_cache)
    create_dirtree_without_files(ini_path, bini_cache)   
    executor = ThreadPoolExecutor(max_workers = 128)

    for input_file in glob.glob(f"{ini_path}\\**\\*.ini", recursive=True):
            output_file = input_file.replace(ini_path, bini_cache)
            executor.submit(convert_file_ini_bini, input_file, output_file)

    executor.shutdown()
