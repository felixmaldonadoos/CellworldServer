import tcp_messages as tcp
import cellworld as cw

client = tcp.MessageClient()
# client.connect(ip="172.26.176.129", port=4790)
client.connect(ip='172.30.127.68', port=4790)

def myprint(msg):
    print(msg)

def send_basic(client, header:str=None, body=None):
    if client is None: 
        print("client is None"); 
    
    print(f"sending: {header} | {body}")
    client.router.add_route(header, myprint )
    client.send_message(tcp.Message(header=header, body=body))
    return client 

client = send_basic(client, "reset", None)

def show_move(message):
    print(message)
    pass

if client.subscribe():
    print("subscribed")
else:   
    print("not subscribed")

client.router.add_route("prey_step", myprint)
# client.router.add_route("predator_step", myprint)
client.router.on_unrouted = myprint

import time
import numpy as np

while True:
    time.sleep(1)
    msg = tcp.Message(header="prey_step", body=cw.Location(1,1)*np.random.randint(0, 1))
    client.send_message(msg)
    print(msg)
    pass

print("done")