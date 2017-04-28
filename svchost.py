#!/usr/bin/env python

import ClientConnector

import imp
import os
import sys

root="."
if len(sys.argv)>1:
    root=sys.argv[1]

client_connector = ClientConnector.connect("client", "password")

print "\nScanning %s for services..." %root
file_list=[]
for root, dirs, files in os.walk(root, topdown=False):
    for name in files + dirs:
        if name.endswith(".py"):
            file_list.append(os.path.join(root, name))

services_count=0
for filename in file_list:
    pyfile = imp.load_source(filename, filename)
    for methodname in dir(pyfile):
        if not methodname.startswith("_"):
            if methodname.endswith("_receive"):
                print "Attaching listener "+filename+":"+methodname
                client_connector.listen(getattr(pyfile, methodname))
                services_count+=1
            if methodname.endswith("_publish"):
                print "Attaching publisher "+filename+":"+methodname
                client_connector.publish(getattr(pyfile, methodname))
                services_count+=1
print "Attached "+str(services_count)+" service(s)."
client_connector.hang()
