# Starts Freelancer from FL_PATH and tails FLSpew. Terminates the process when 'Trailing References' are detected and pipes the crash offset into the console if the game closes unexpectedly
import os
import threading
import time, datetime
import urllib.request, json
import win32evtlog
from subprocess import Popen
import pythoncom, wmi
import re

from utils import *

flspew_log_path = f"{os.getenv('LOCALAPPDATA')}\\Freelancer"
def follow(file):
    # Seek the end of the file
    file.seek(0)
    # Start infinite loop
    while True:
        global stop_threads
        if stop_threads is True:
            raise SystemExit # TODO: Maybe call exit(exitcode_integer) here?
        # Read the whole file
        line = file.readline()
        # Sleep if file hasn't been updated
        if not line:
            time.sleep(0.5)
            continue

        if "C:\\work\\builds\\dalibs\\dalibs-build\\build\\Src\\RenderPipeline\\DX8\\dx8_shader_inl.h(84) : WARNING:General:flush_stream_source: D3DERR_INVALIDCALL" in line:
            continue

        if "for item (0x81837304)" in line:
            linetime = time.strftime("%Y%m%d-%H:%M:%S")
            regexp = re.compile(r'\{.*?\}')
            line = regexp.findall(line)
            print(bcolors.OKCYAN + f"[{linetime}] C:\\build-tools\\python\\freelancer.py(32) : *** DEBUG: Created object {line[0].strip(r'{}')}" + bcolors.ENDC)
            continue

        if "ERROR: ArchDB::Get(0) failed" in line:
            continue

        if "DEBUG" in line:
            line = bcolors.OKCYAN + line + bcolors.ENDC

        if "WARNING" in line:
            line = bcolors.WARNING + line + bcolors.ENDC
            
        if "ERROR" in line:
            line = bcolors.FAIL + line + bcolors.ENDC
        
        if "E:\\FL\\Scratch\\Source\\DALib\\DALib.cpp(376) : WARNING:General:******* DA SYSTEM: trailing references *******" in line:
            yield line
            global trailing_references
            trailing_references = True
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            fl_running_end_time = time.perf_counter() 
            print(bcolors.HEADER + f"Stopping {freelancer_name}, PID {freelancer_pid} at {current_time} gracefully, the application has been running for {fl_running_end_time - fl_running_start_time:0.4f} seconds" + bcolors.ENDC)
            # If the process has somehow stuck around, kill it. If not, don't throw a confusing error.
            os.system(f"taskkill /F /PID {freelancer_pid} 2>NUL")
            stop_threads = True
            raise SystemExit # TODO: Maybe call exit(exitcode_integer) here?
        yield line

def start_freelancer():    
    # Shelve last log file
    try:
        last_log_timestamp = os.path.getmtime(flspew_log_path+"\\FLSpew.txt")
        os.rename(src = flspew_log_path+"\\FLSpew.txt", dst = flspew_log_path+"\\FLSpew_"+str(datetime.datetime.fromtimestamp(last_log_timestamp).isoformat()).replace(":", "_")+".txt")
    except FileNotFoundError:
        raise
    
    # Start FL
    print(bcolors.OKBLUE + f"Starting Freelancer in windowed mode..." + bcolors.ENDC)
    fl_proc = Popen([f"{fl_path}\\Freelancer.exe", "-w"], shell=True)
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    global freelancer_pid 
    freelancer_pid = fl_proc.pid
    global fl_running_start_time
    fl_running_start_time = time.perf_counter()
    print(bcolors.OKGREEN + f"Started freelancer.exe with PID {freelancer_pid} at {current_time}" + bcolors.ENDC)

    if tail_flspew == True:
        # Wait until file creation
        while not os.path.exists(flspew_log_path+"\\FLSpew.txt"):
            print(bcolors.OKBLUE + "Waiting for FLSpew creation ..." + bcolors.ENDC)
            time.sleep(0.5)
        # Follow, iterating over the generator
        log_file = open(flspew_log_path+"\\FLSpew.txt")
        log_lines = follow(log_file)
        for line in log_lines:
            print(line, end="")

# This function grabs the latest Freelancer crash event it can find that matches the PID of the tailed and launched thread. It's possible that this might grab a duplicate PID, but it works through the first 100 events and will grab the latest one with a PID matching the freelancer_pid variable so the chances of it grabbing the wrong one are pretty slim.
def fetch_crash_offset():
    global stop_threads
    server = "localhost"
    logtype = "Application"
    hex_pid = hex(freelancer_pid).lstrip("0x")
    hand = win32evtlog.OpenEventLog(server,logtype)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
    iterate = 0
    data = False
    while iterate < 100:
        events = win32evtlog.ReadEventLog(hand, flags,0)
        iterate =  iterate + 1
        if events:
            for event in events:           
                    if event.EventID == 1000 and "Freelancer.exe" and f"{hex_pid}" in event.StringInserts:
                        data = event.StringInserts
                        iterate = 101
                        break

    if data:
        print("Time Generated:", event.TimeGenerated)
        print("Source Name:", event.SourceName)
        print("Event ID:", event.EventID)
        print(f"Exception Code: 0x{data[6]}")
        print(f"Faulting Application Name: {data[0]}, version {data[1]}, PID {int(data[8], 16)}")
        print(f"Faulting Application Path: {data[10]}")
        print(bcolors.BOLD + f"Faulting Module Name: {data[3]}, version {data[4]}" + bcolors.ENDC)
        print(f"Faulting Module Path: {data[11]}")
        print(bcolors.BOLD + f"Fault Offset: 0x{data[7]}" + bcolors.ENDC)                            

        full_offset = "0x" + data[7].lower()
        faulting_module = data[3].lower()

        try:
            print(bcolors.HEADER + "Attempting to fetch JSON crash information from the Starport KnowledgeBase..." + bcolors.ENDC)
            with urllib.request.urlopen("https://raw.githubusercontent.com/TheStarport/KnowledgeBase/master/static/payloads/crash-offsets.json") as url:
                crash_data = json.load(url)
        except:
            print(bcolors.FAIL + "Unable to reach the Starport Knowledgebase, Falling back on local file..." + bcolors.ENDC)
            file = open("crash_offsets.json")
            crash_data = json.load(file)

        for r in crash_data:
            if (r["offset"].lower() == full_offset) and (r["moduleName"].lower() == faulting_module):
                print(bcolors.OKBLUE + f"Offset Description: {r['description']}" + bcolors.ENDC)
                print(bcolors.OKBLUE + f"Found By: {r['author']}" + bcolors.ENDC)
                from datetime import datetime
                print(bcolors.OKBLUE + f"Date Added: {datetime.fromtimestamp(r['dateAdded'])}" + bcolors.ENDC)
                print(bcolors.FAIL + "For further debugging, please reference the fault offset and faulting module name against https://wiki.the-starport.net/wiki/fl-binaries/crash-offsets" + bcolors.ENDC)
                stop_threads = True 
                raise SystemExit # TODO: Maybe call exit(exitcode_integer) here?
            
        print(bcolors.FAIL + f"No crash offset at {full_offset} in {faulting_module} has been documented previously. Please determine the cause of the crash and submit an update to the Starport KnowledgeBase" + bcolors.ENDC)
        stop_threads = True    
        raise SystemExit # TODO: Maybe call exit(exitcode_integer) here?
        
    else:
        print(bcolors.FAIL + f"No crash offset corresponding to PID {freelancer_pid} was found. It\'s likely the Freelancer process was killed manually, or something else unusual has happened. Please check your Windows Application logs if it's not clear what killed the process in this instance." + bcolors.ENDC)
        stop_threads = True    
        raise SystemExit # TODO: Maybe call exit(exitcode_integer) here?

def alive_check(wmiC, pid):        
    for process in wmiC.Win32_Process():
        if process.ProcessId == pid:
            return True
    return False

def crash_check():
    global stop_threads
    pythoncom.CoInitialize()
    wmiC = wmi.WMI()
    while True:
        time.sleep(1)
        global trailing_references
        if trailing_references != True and alive_check(wmiC, freelancer_pid) is False:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            fl_running_end_time = time.perf_counter() 
            print(bcolors.FAIL + f"{freelancer_name}, PID {freelancer_pid} has stopped unexpectedly at {current_time} after running for {fl_running_end_time - fl_running_start_time:0.4f} seconds. Fetching crash event from Application logs... " + bcolors.ENDC)
            fetch_crash_offset()
            stop_threads = True
            raise SystemExit # TODO: Maybe call exit(exitcode_integer) here?
        if trailing_references is True:
            stop_threads = True
            raise SystemExit # TODO: Maybe call exit(exitcode_integer) here?
        if stop_threads is True:
            raise SystemExit # TODO: Maybe call exit(exitcode_integer) here?

def start_freelancer_main():
    fl_tailed_process = threading.Thread(target=start_freelancer)
    fl_tailed_process.start()
    fl_crash_handler = threading.Thread(target=crash_check)
    fl_crash_handler.start()