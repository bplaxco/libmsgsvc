#! /usr/bin/env python

from libmsgsvc.server.Tracker import Tracker


if __name__ == "__main__":
    tracker = Tracker("./conf")
    tracker.listen()
