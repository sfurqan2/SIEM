from winevt import EventLog

from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
import atexit
import os
import threading
import win32file
import win32con
from dataclasses import dataclass
from typing import List
import subprocess
import json
import time
import datetime

app = Flask(__name__)
app.config["DEBUG"] = True

cors = CORS(app, resources={r"/*": {"origins": "*"}})


alerts = []
stopThreads = False

ACTIONS = {
    1: "Created",
    2: "Deleted",
    3: "Updated",
    4: "Renamed to ",
    5: ""
}

diskFiles = []
folderFiles = []
t1 = None
t2 = None
t3 = None

FILE_LIST_DIRECTORY = 0x0001

def watchFile(dirname, stopThreads, removable_disk = False):
    print(dirname)
    path_to_watch = dirname

    hDir = win32file.CreateFile(
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )
    while 1:
        if(stopThreads):
            break;

        results = win32file.ReadDirectoryChangesW(
            hDir,
            1024,
            True,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
            # win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
            # win32con.FILE_NOTIFY_CHANGE_SIZE |
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
            # win32con.FILE_NOTIFY_CHANGE_SECURITY,
            None,
            None
        )

        for action, file in results:
            full_filename = os.path.join(path_to_watch, file)
            if action == 4:
                print(full_filename, ACTIONS.get(action, "Unknown"), end='')
            else :
                print(full_filename,ACTIONS.get(action, "Unknown"))
                if action != 5:
                    if removable_disk:
                        diskFiles.append([full_filename, action, time.time(), datetime.datetime.fromtimestamp(time.time())])
                    else:
                        folderFiles.append([full_filename, action, time.time(), datetime.datetime.fromtimestamp(time.time())])

@dataclass
class Drive:
    letter: str
    label: str
    drive_type: str

def list_drives() -> List[Drive]:
    
    proc = subprocess.run(
        args=[
            'powershell',
            '-noprofile',
            '-command',
            'Get-WmiObject -Class Win32_LogicalDisk | Select-Object deviceid,volumename,drivetype | ConvertTo-Json'
        ],
        text=True,
        stdout=subprocess.PIPE
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        print('Failed to enumerate drives')
        return []
        
    devices = json.loads(proc.stdout)

    drive_types = {
        0: 'Unknown',
        1: 'No Root Directory',
        2: 'Removable Disk',
        3: 'Local Disk',
        4: 'Network Drive',
        5: 'Compact Disc',
        6: 'RAM Disk',
    }

    removables = []

    for d in devices:
        if d['drivetype'] == 2:
            removables.append(Drive(
                letter = d['deviceid'],
                label = d['volumename'],
                drive_type = drive_types[d['drivetype']]
            ))
    
    return removables

def check_device_change(old_devices, stopThreads):
    devices = list_drives()
    count = len(devices) - len(old_devices)
    global t2

    if count > 0:
        print('added: {}'.format(devices[0]))
        t2 = threading.Thread(target = watchFile, args=(devices[0].letter +"/", stopThreads, True,))
        t2.start()

    if count < 0:
        print('removed: {}'.format(old_devices[0]))
        if t2 is not None:
            t2.join()
            t2 = None
        
    return devices

def removable_storage_listener(stopThreads):
    old_devices = []
    while True:
        if stopThreads:
            break
        old_devices = check_device_change(old_devices, stopThreads)
        
        time.sleep(1)

def take_time(elem):
    return elem[2]


def get_filename(full_name):
    head, tail = os.path.split(full_name)
    return tail

def checkAlerts(stopThreads):
    global diskFiles
    global folderFiles

    while 1:
        if stopThreads:
            break

        diskFiles.sort(key=take_time, reverse=True)
        folderFiles.sort(key=take_time, reverse=True)

        for r_dir in diskFiles:
            for f_dir in folderFiles:
                if r_dir[2] >= f_dir[2] - 5 and r_dir[2] <= f_dir[2] + 5:
                    if r_dir[1] == 1 and f_dir[1] == 2:
                        if get_filename(r_dir[0]) == get_filename(f_dir[0]):
                            alerts.append({
                                "filename": get_filename(r_dir[0]),
                                "time": r_dir[3],
                                "details": [r_dir, f_dir]
                            })

        diskFiles = []
        folderFiles = []

        time.sleep(1)


t1 = threading.Thread(target = watchFile, args=("C:/Test", stopThreads, ))
t3 = threading.Thread(target = removable_storage_listener, args=(stopThreads,))
t4 = threading.Thread(target = checkAlerts, args=(stopThreads,))

t1.start()
t3.start()
t4.start()

def by_time(elem):
    return elem["time"]

@app.route('/', methods=['GET'])
def getEvents():

    f_alerts = []

    alerts.sort(key=by_time, reverse=True)

    new_alert = {"details": [], "files": [], "time": ""}

    for i in range(len(alerts)):

        new_alert["details"].extend(alerts[i]["details"])
        new_alert["files"].append(alerts[i]["filename"])
        new_alert["time"] = alerts[i]["time"]

        if i + 1 < len(alerts):
            print(alerts[i])
            if alerts[i]["details"][0][2] <= alerts[i+1]["details"][0][2] + 2 and alerts[i]["details"][0][2] >= alerts[i+1]["details"][0][2] - 2:
                # new_alert["details"].extend(alerts[i+1]["details"])  
                # new_alert["files"].append(alerts[i + 1]["filename"])
                pass
            else:
                f_alerts.append(new_alert)
                new_alert = {"details": [], "files": [], "time": ""}
                if(i == len(alerts) - 1):
                    new_alert["details"].extend(alerts[i+1]["details"])  
        else:
            f_alerts.append(new_alert)

    print(f_alerts)

    return jsonify(f_alerts)
    

# def handleEvent(action, pContext, event):
#     evt = {}
#     if hasattr(event, "EventData"):
#         if hasattr(event.EventData, "Data"):
#             if event.EventData.Data[1].cdata == "Furqan Saeed":
#                 evt["EventID"] = event.EventID
#                 for item in event.EventData.Data:
#                     if item["Name"] == "SubjectUserName" or item["Name"] == "ObjectName" or item["Name"] == "HandleId" or item["Name"] == "AccessMask":
#                         evt[item["Name"]] = item.cdata
#                 events.append(evt)

# cb = EventLog.Subscribe("Security", "Event/System[EventID=4663 or EventID=4660]", handleEvent)

# @app.route('/', methods=['GET'])
# def getEvents():
#     evts = []
#     evts2 = {}

#     for event in events:         
#         if event["EventID"] == 4663:
#             if event["AccessMask"] == "0x10000":
#                 evts.append(event)

#     # for evt in evts:
#     #     evt["ObjectName"] = evts2[evt["HandleId"]]["ObjectName"]
    
#     return jsonify(evts)



# def unsubscribeEvent():
#     cb.unsubscribe()
def closeThreads():
    global stopThreads
    print("TRYING TO CLOSE")
    stopThreads = True
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    print("\nProgram exiting gracefully")

atexit.register(closeThreads)