from libmsgsvc import MsgService, on_recv
import sys
import time


def greet_handler(svc, msg):
    if msg == "hello":
        svc.send_message("Well hello there!")
    elif msg == "Well hello there!":
        print(msg)


if __name__ == "__main__":
    # Connection info
    password = "somepassword"
    server = "irc.freenode.net"
    print "Connecting to " + server
    svc = MsgService(server, password, sys.argv[1])

    on_recv(svc, greet_handler)

    while True:
        value = raw_input().strip()

        if value == "exit":
            sys.exit()
        else:
            svc.send_message(value)

