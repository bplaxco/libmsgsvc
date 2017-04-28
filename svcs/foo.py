def msgprinter_receive(bus, msg):
    print msg
    print msg.to_dict
    print msg.get_data()

tick=0
from time import sleep

def tick_publish(bus):
    global tick
    sleep(10)
    tick+=10
    bus.send_data(str(tick)+" seconds have passed.")
