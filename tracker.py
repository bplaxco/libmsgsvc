#! /usr/bin/env python

from libmsgsvc.server.Tracker import Tracker


if __name__ == "__main__":
    tracker = Tracker("./tracker_conf")
    tracker.listen()