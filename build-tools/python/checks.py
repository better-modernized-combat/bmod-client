# Looks for Freelancer.exe and terminates the process if it exists.
import wmi
import time

from utils import bcolors
from utils import os

def validate_process_stopped():
    wmic = wmi.WMI()
    print(bcolors.OKBLUE + "Searching for instances of Freelancer.exe..." + bcolors.ENDC)
    found_freelancer = False
    for process in wmic.Win32_Process():
        if "freelancer" in process.Name.lower():
            found_freelancer = True
            process_name = process.Name
            process_id = process.ProcessId
            print(bcolors.WARNING + "Found {}, PID {}.".format(process_name, process_id) + bcolors.ENDC)
            print(bcolors.OKBLUE + "Stopping {}, PID {}...".format(process_name, process_id) + bcolors.ENDC)
            try:
                process.Terminate()
                time.sleep(3)
                print(bcolors.OKGREEN + "{}, PID {} stopped, proceeding".format(process_name, process_id) + bcolors.ENDC)
            except SystemExit as exit:
                print(bcolors.FAIL + "Unable to stop {}, PID {}, halting the build script.".format(process_name, process_id) + bcolors.ENDC)
                raise exit

    if not found_freelancer:
        print(bcolors.OKGREEN + f"No running instances of Freelancer found, proceeding" + bcolors.ENDC)


def validate_path():
    if os.getenv("FL_PATH") is None:
        print(bcolors.WARNING + "No FL_PATH environment variable has been found. Please enter the full path for the EXE folder of the Freelancer instance you wish to work with. This environment variable will only persist for the duration of this session and should be set permanently using the System.Environment class." + bcolors.ENDC)
        fl_path = input()
        os.environ["FL_PATH"] = fl_path
        print(bcolors.OKGREEN + "The FL_PATH environment variable has been set to '{}'".format(fl_path) + bcolors.ENDC)

    else:
        fl_path = os.environ["FL_PATH"] 
        print(bcolors.BOLD + "The FL_PATH environment variable is set to '{}'".format(fl_path) + bcolors.ENDC)