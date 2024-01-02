# Looks for Freelancer.exe and terminates the process if it exists.
import wmi

from utils import *

def validate_process_stopped():
    wmiC = wmi.WMI()
    print(bcolors.OKBLUE + f"Searching for instances of Freelancer.exe..." + bcolors.ENDC)
    found_freelancer = False
    for process in wmiC.Win32_Process():
        if "freelancer" in process.Name.lower():
            found_freelancer = True
            print(bcolors.WARNING + f"Found {process.Name}, PID {process.ProcessId}." + bcolors.ENDC)
            print(bcolors.OKBLUE + f"Stopping {process.Name}, PID {process.ProcessId}..." + bcolors.ENDC)
            try:
                process.Terminate()
                print(bcolors.OKGREEN + f"{process.Name}, PID {process.ProcessId} stopped, proceeding" + bcolors.ENDC)
            except:
                print(bcolors.FAIL + f"Unable to stop {process.Name}, PID {process.ProcessId}, halting the build script." + bcolors.ENDC)
                raise SystemExit

    if not found_freelancer:
        print(bcolors.OKGREEN + f"No running instances of Freelancer found, proceeding" + bcolors.ENDC)


def validate_path():
    if os.getenv("FL_PATH") is None:
        print(bcolors.WARNING + f"No FL_PATH environment variable has been found. Please enter the full path for the EXE folder of the Freelancer instance you wish to work with. This environment variable will only persist for the duration of this session and should be set permanently using the System.Environment class." + bcolors.ENDC)
        fl_path = input()
        os.environ["FL_PATH"] = fl_path
        print(bcolors.OKGREEN + f"The FL_PATH environment variable has been set to '{fl_path}'" + bcolors.ENDC)

    else:
        fl_path = os.environ["FL_PATH"] 
        print(bcolors.BOLD + f"The FL_PATH environment variable is set to '{fl_path}'" + bcolors.ENDC)