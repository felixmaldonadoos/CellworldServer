print("starting")
import tcp_messages as tcp
import cellworld as cw
import time
import numpy as np

print("creating client")
client = tcp.MessageClient()
# client.connect(ip="172.26.176.129", port=4790)
client.connect(ip='192.168.137.13', port=4790) # vr backpack

def myprint(msg):
    print(msg)

def show_move(message):
    print(message)
    pass

if client.subscribe():
    print("subscribed")
else:   
    print("not subscribed")

client.router.add_route("prey_step", myprint)
client.router.add_route("reset", myprint)
# client.router.add_route("predator_step", myprint)
client.router.on_unrouted = myprint

client.send_message(tcp.Message(header="reset",body=""))

while True:
    time.sleep(1)
    # client.send_message(msg)
    # print(msg)
    # msg = tcp.Message(header="prey_step", body=cw.Location(1,1)*np.random.randint(0, 1))
    msg = tcp.Message(header="prey_step", body=cw.Step(location=cw.Location(1,1)*np.random.randint(0, 1)))
    client.send_message(msg)
    # print(msg)
    pass

print("done")