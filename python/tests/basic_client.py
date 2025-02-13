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
if not client.connect(ip='192.168.1.5', port=4791): 
    print('failed to connect')
    exit(0)
else: 
    print('connected')


client.router.add_route("prey_step", myprint)
client.router.add_route("on_capture", _on_capture_)
client.router.add_route("reset", myprint)
client.router.add_route("reset_response", _reset_response_)
client.router.on_unrouted = myprint

while True:
    msg = tcp.Message(header="reset", body='client_test')
    if client.send_message(msg):
        print("sent")
    else:
        print("failed")