import glob
import subprocess
import shutil

from concurrent.futures import ThreadPoolExecutor

from utils import *

lua_path = f"{root_copy_path}\\mod-assets\\DATA\\"
thorn_cache = f"{root_copy_path}\\.thorn-cache\\"

def convert_file_lua_thorn(input_file, output_file):
    return_code = subprocess.Popen(["build-tools\\thorn.exe","-c", "-o", output_file, input_file]).wait()
    if return_code !=0:
        print(bcolors.FAIL + f"Failed to convert {input_file}" + bcolors.ENDC)

def lua_to_thorn_thread():
    cache_exists = os.path.isdir(thorn_cache)
    if cache_exists == True:
         shutil.rmtree(thorn_cache)
    create_dirtree_without_files(lua_path, thorn_cache)   
    executor = ThreadPoolExecutor(max_workers = 128)

    for input_file in glob.glob(f"{lua_path}\\**\\*.lua", recursive=True):
            output_file = input_file.replace(lua_path, thorn_cache).replace(".lua", "")
            executor.submit(convert_file_lua_thorn, input_file, output_file)

    executor.shutdown()
