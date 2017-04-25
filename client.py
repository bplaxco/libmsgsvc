#! /usr/bin/env python

from libmsgsvc import svc_connect, svc_on_recv
import sys
import time


def print_handler(svc, msg):
    print(msg["data"])


if __name__ == "__main__":
    # Connection info
    info = sys.argv[1]
    print "Connecting to " + info
    svc = svc_connect(info, debug=True)

    # Start clearing the buffer
    svc_on_recv(svc, print_handler)
    time.sleep(2)
    svc.join()

    while True:
        value = raw_input().strip()

        if value == "exit":
            sys.exit()
        else:
            svc.send_message(value)
