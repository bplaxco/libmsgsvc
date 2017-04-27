#!/usr/bin/env python
import imp
import json
import os
import sys

from AbstractClient import AbstractClient

def receive(bus, msg):
    svc=None
    try:
#        print msg
        msg["data"]=json.loads(msg["data"])
        svc=msg["data"]["pirclug_svc"]
        print "Pirclug message received.  Service is: "+svc
        filename=svc+".py"
        filename=os.path.join(os.getcwd(), sys.argv[1], filename)
        pyfile = imp.load_source(filename, filename)
        pyfile.receive(msg, bus)
    except Exception as e:
#        print e
#        print("Received a non-pirclug message.")
        pass

#
def main():
    pass
AbstractClient("svchost", "password", receive, debug=False).begin()
