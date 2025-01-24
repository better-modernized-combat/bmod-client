import json
import distutils.dir_util
import time
import os

with open('paths.json', 'r') as file:
    bmod_paths_json_str = file.read()

bmod_paths_data = json.loads(bmod_paths_json_str)
root_copy_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..'))

asset_copy_start_time = time.perf_counter() 

print(f'Copying files from {root_copy_path}/mod-assets/ to {bmod_paths_data['copy_path']}.')
distutils.dir_util.copy_tree(f'{root_copy_path}/mod-assets/EXE', f'{bmod_paths_data['copy_path']}/EXE')
distutils.dir_util.copy_tree(f'{root_copy_path}/mod-assets/DATA', f'{bmod_paths_data['copy_path']}/DATA')
distutils.dir_util.copy_tree(f'{root_copy_path}/mod-assets/DLLS', f'{bmod_paths_data['copy_path']}/DLLS')
asset_copy_end_time = time.perf_counter() 
print(f"Asset files copied over in {asset_copy_end_time - asset_copy_start_time:0.4f} seconds")

os.system('lutris lutris:rungame/freelancer-bmod-dev')