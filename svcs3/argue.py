def invoke(msg, bus):
    bus.send_message("Bar is better than foo!  What say you?")
    bus.send_message('{"pirclug_svc": "foo"}')
