from winevt import EventLog

from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
import atexit

app = Flask(__name__)
app.config["DEBUG"] = True

cors = CORS(app, resources={r"/*": {"origins": "*"}})

events = []

def handleEvent(action, pContext, event):
    evt = {}
    if hasattr(event, "EventData"):
        if hasattr(event.EventData, "Data"):
            if event.EventData.Data[1].cdata == "Furqan Saeed":
                evt["EventID"] = event.EventID
                for item in event.EventData.Data:
                    if item["Name"] == "SubjectUserName" or item["Name"] == "ObjectName" or item["Name"] == "HandleId" or item["Name"] == "AccessMask":
                        evt[item["Name"]] = item.cdata
                events.append(evt)

cb = EventLog.Subscribe("Security", "Event/System[EventID=4663 or EventID=4660]", handleEvent)

@app.route('/', methods=['GET'])
def getEvents():
    evts = []
    evts2 = {}

    for event in events:         
        if event["EventID"] == 4663:
            if event["AccessMask"] == "0x10000":
                evts.append(event)

    # for evt in evts:
    #     evt["ObjectName"] = evts2[evt["HandleId"]]["ObjectName"]
    
    return jsonify(evts)



def unsubscribeEvent():
    cb.unsubscribe()

atexit.register(unsubscribeEvent)