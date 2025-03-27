print("starting")
import tcp_messages as tcp
import cellworld as cw
import time
import numpy as np
from PolygonLib import PolygonHab

print("creating client")
client = tcp.MessageClient()
client.connect(ip='127.0.0.1', port=4791)

def myprint(msg):
    print(f'Unrouted: {msg}')

def show_move(message):
    print(message)
    pass
    if client.subscribe():
        print("subscribed")
    else:   
        print("not subscribed")

def _reset_response_(msg:tcp.Message = None):
    print(f'_reset_response_: {msg.body}')
    global bCanUpdate
    if msg.body == 'success':
        bCanUpdate = True
    else: 
        print('failed')

def _on_capture_(msg:tcp.Message = None):
    print(f'[ _on_capture_ ]')
    global bCanUpdate
    bCanUpdate = False
    time.sleep(2)
    client.send_request(tcp.Message(header='reset',body=''))
    bCanUpdate = True

client.router.add_route("prey_step", myprint)
client.router.add_route("on_capture", _on_capture_)
client.router.add_route("reset", myprint)
client.router.add_route("reset_response", _reset_response_)
client.router.on_unrouted = myprint

def stop_and_reset():
    print('sending reset 1')
    msg = tcp.Message(header='reset',body='')
    client.send_message(msg)
    
    print('sending stop')
    time.sleep(1)
    msg = tcp.Message(header='stop',body='')
    client.send_message(msg)

    print('sending reset 2')
    time.sleep(1)
    msg = tcp.Message(header='reset',body='')
    client.send_message(msg)
    return 

def reset_and_stop_once(client):
    if not client.connected:
        print('[reset_and_stop_once] client not connected')
        return
    print('[reset_and_stop_once] sending stop')
    time.sleep(1)
    msg = tcp.Message(header='stop',body='')
    client.send_message(msg)

    print('[reset_and_stop_once] sending reset 1')
    client.send_message(tcp.Message(header='reset',body=''))

# create path to evaluate 
N = 1000
step_size = 0.01
fs = 30 # 90 Hz
T = 1/fs 

path = PolygonHab().generate_path(N=N, step_size=step_size)
# path = PolygonHab().generate_path_finish(N=N, step_size=0.1)

print('== starting main loop ==')
print(f'- fs = {fs} | T = {T:0.4f} | N = {N} | step_size = {step_size}\n')

bCanUpdate = False

t0 = time.time()
i = 0
loops = 0

print(f'Subscription response: {client.subscribe()}')
print('Sending: Initial reset')

if client.send_message(tcp.Message(header='reset',body='')):
    print("Sent reset OK")

while True:
    if bCanUpdate:
        time.sleep(T)
        index = i % len(path)
        x = path[index].x
        y = path[index].y
        tnow = time.time()-t0
        msg = tcp.Message(header="prey_step", body=cw.Step(location=cw.Location(x,y),time_stamp=tnow, frame=i))
        client.send_message(msg)
        print(f'frame sent: {i}')
        i += 1
        if (i % N == 0):
            loops+=1
            te = time.time() - t0
            print(f'Finished path (N={N}) | loops completed: {loops} | fs = {i/te}')
            print('closing')
            client.send_message(tcp.Message(header='stop',body=''))
            print('sleeping for 3 seconds')
            time.sleep(3)
            print('resetting')
            # client.send_request(tcp.Message(header='reset',body=''))
            client.send_message(tcp.Message(header='reset',body=''))
            # reset loop loggers 
            t0 = time.time()
            i = 0

print("done")
