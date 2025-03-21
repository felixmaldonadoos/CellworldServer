print("starting")
import tcp_messages as tcp
import cellworld as cw
import time
import numpy as np
from PolygonLib import PolygonHab

def myprint(msg):
    print(f'Unrouted: {msg}')

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

print("creating client")
client = tcp.MessageClient()
if not client.connect(ip='192.168.1.2', port=4791): 
    print('failed to connect')
    exit(0)
else: 
    print('connected')

client.router.add_route("prey_step", myprint)
client.router.add_route("on_capture", _on_capture_)
client.router.add_route("reset", myprint)
client.router.add_route("reset_response", _reset_response_)
client.router.on_unrouted = myprint

input('enter to set vr origin')
s = f'{0},{0},{0},{1}'
msg = tcp.Message(header="set_vr_origin", body=s )
client.send_message(msg)
while True:
    # originA = [0,0]
    # originB = [0,1]
    msg = tcp.Message(header="prey_step", body=cw.Step(location=(0.5,0.5)))
    if client.send_message(msg):
        time.sleep(0.1)
        print("sent")
    else:
        print("failed")