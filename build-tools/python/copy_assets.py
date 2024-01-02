# Sets the root copy path and copies assets over from the mod-assets folder to the install located at the FL_PATH variable location.
import distutils.dir_util
import shutil
import time

from bini import *
from thorn import *
from utils import *

fl_path = os.environ["FL_PATH"] 

def copy_files():
    print(bcolors.OKBLUE + f'Copying asset files from {root_copy_path}\\mod-assets to installation located at {fl_path}' + bcolors.ENDC)
    asset_copy_start_time = time.perf_counter() 
    distutils.dir_util.copy_tree(f'{root_copy_path}\\mod-assets\\EXE', f'{fl_path}')
    distutils.dir_util.copy_tree(f'{root_copy_path}\\mod-assets\\DATA', f'{fl_path}\\..\\DATA')
    distutils.dir_util.copy_tree(f'{root_copy_path}\\mod-assets\\DLLS', f'{fl_path}\\..\\DLLS')
    asset_copy_end_time = time.perf_counter() 
    print(bcolors.OKGREEN + f"Asset files copied over in {asset_copy_end_time - asset_copy_start_time:0.4f} seconds" + bcolors.ENDC)

def copy_thorn_cleanup_cache():
    print(bcolors.OKBLUE + f'Copying encoded Thorn files from the cache to {fl_path}' + bcolors.ENDC)
    distutils.dir_util.copy_tree(thorn_cache, f'{fl_path}\\..\\DATA')
    print(bcolors.OKBLUE + f'Encoded Thorn files copied from the cache to {fl_path}. Cleaning up...' + bcolors.ENDC)
    try:
        shutil.rmtree(thorn_cache)
        print("Removed the Thorn cache, cleanup complete.")
    except:
        print(bcolors.FAIL + "Unable to remove the Thorn cache. Please check the folder permissions and try again, or cleanup manually." + bcolors.ENDC)

def copy_bini_cleanup_cache():
    print(bcolors.OKBLUE + f'Copying encoded BINI files from the cache to {fl_path}' + bcolors.ENDC)
    distutils.dir_util.copy_tree(bini_cache, f'{fl_path}\\..\\DATA')
    print(bcolors.OKBLUE + f'Encoded BINI files copied from the cache to {fl_path}. Cleaning up...' + bcolors.ENDC)
    try:
        shutil.rmtree(bini_cache)
        print("Removed the BINI cache, cleanup complete.")
    except:
        print(bcolors.FAIL + "Unable to remove the BINI cache. Please check the folder permissions and try again, or cleanup manually." + bcolors.ENDC)
