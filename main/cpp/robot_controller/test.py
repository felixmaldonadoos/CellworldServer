print("starting")
import tcp_messages as tcp
import cellworld as cw
import time
import numpy as np
from PolygonLib import PolygonHab
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

# create path to evaluate 
N = 1000
step_size = 0.01
fs = 90 # 90 Hz
T = 1/fs 
i = 0
loops = 0

path = PolygonHab().generate_path(N=N, step_size=step_size)

t0 = time.time()

print('== starting main loop ==')
print(f'- fs = {fs} | T = {T:0.4f} | N = {N} | step_size = {step_size}\n')
while True:
    time.sleep(T)
    index = i % len(path)
    x = path[index].x
    y = path[index].y
    msg = tcp.Message(header="prey_step", body=cw.Step(location=cw.Location(x,y)))
    client.send_message(msg)
    i += 1
    if (i % N == 0):
        loops+=1
        te = time.time() - t0
        print(f'Finished path (N={N}) | loops completed: {loops} | fs = {i/te}')
        client.send_message(msg)

        # reset loop loggers 
        t0 = time.time()
        i = 0

print("done")
