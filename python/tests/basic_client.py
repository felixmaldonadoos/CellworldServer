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

print("creating client")
client = tcp.MessageClient()
client.connect(ip='192.168.1.2', port=4791) 
client.router.add_route("prey_step", myprint)
client.router.add_route("on_capture", _on_capture_)
client.router.add_route("reset", myprint)
client.router.add_route("reset_response", _reset_response_)
client.router.add_route("set_origin_response", _reset_response_)
client.router.on_unrouted = myprint

input('enter to set vr origin')
msg = tcp.Message(header="set_vr_origin", body='0.5,0.5,1,0.5')
client.send_message(msg)
print(f'sent: {msg}')
time.sleep(3)
msg = tcp.Message(header="reset", body='')
client.send_message(msg)
# # msg = tcp.Message(header="get_cell_locations", body='')s
# print(f'sent: {msg}')
# print('sleeping 2 seconds before sending steps...')
# time.sleep(2)
# client.send_message(tcp.Message(header='reset',body=''))
time.sleep(0.5)
frame = 0
while True:
    msg = tcp.Message(header="prey_step", body=cw.Step(agent_name='prey',frame=frame))
    client.send_message(msg)
    time.sleep(0.01)
    frame +=1 