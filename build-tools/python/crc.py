#Invokes createid.exe at runtime to resolve hashes

import subprocess
from utils import *

data_path = f"{fl_path}\\..\\DATA"

def generate_hashes():
    print(bcolors.OKBLUE + f"Generating hashmap.txt..." + bcolors.ENDC)
    f = open("build-tools\\hashmap.txt", "w")
    return_code = subprocess.call([f"{root_copy_path}\\build-tools\\createid.exe", "-s", "-oc", "-h", data_path], stdout=f)
    if return_code != 0:
        print(bcolors.FAIL + f"createid.exe has failed to generate a hashmap. Please consult your Windows Event Logs" + bcolors.ENDC)
    else:
        print(bcolors.OKGREEN + f"hashmap.txt generated successfully" + bcolors.ENDC)