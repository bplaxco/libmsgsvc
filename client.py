import sys
import time
from libmsgsvc import MsgService


if __name__ == "__main__":
    # Connection info
    password = "somepassword"
    server = "irc.freenode.net"
    print "Connecting to " + server
    svc = MsgService(server, password, sys.argv[1])

    while 1:
        msg = svc.recv_message()
        print(msg)

        if msg == "die":
            sys.exit()
        else:
            time.sleep(1)
            svc.send_message("die")
