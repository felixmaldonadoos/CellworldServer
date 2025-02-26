import tcp_messages as tcp
import cellworld as cw
import time


print("starting")

print("creating client")
client = tcp.MessageClient()

ip = "127.0.0.1"
port = 4791

client.connect(ip=ip, port=port)
print(f'Connected to {ip}')

fs = 60  # Hz
step_size = 1 / fs

print(f'Subscription response: {client.subscribe()}')  # subscribe = " i want to listen to subscriptions msgs "
print('Sending: Initial reset')

# if client.send_message(tcp.Message(header='reset', body='')):
#     print("Sent reset OK")

i = 0
t0 = time.time()
print('== starting main loop ==')




# tnow = time.time() - t0
# x,y = 0.5,0.5
# if client.send_message(tcp.Message(header="prey_step", body=cw.Step(location=cw.Location(x, y), time_stamp=tnow, frame=i))):
#     print("Sent prey step")

msg_on_capture = tcp.Message(header="on_capture", body='')

all_msgs = [
    [tcp.Message(header="prey_step", body=cw.Step(location=cw.Location(0.5, 0.5), time_stamp=0, frame=0)), 0],
    [tcp.Message(header="get_occlusions", body=''), 1],
    [tcp.Message(header="get_cell_location", body=''), 1],
    [tcp.Message(header="reset_model", body=''), 1],
    [tcp.Message(header="stop_model", body=''), 1]
]

def show_options(msgs:list=None):
    print('=== select what to send next ===')
    for i in range(len(msgs)):
        if type(msgs[i][0]) != tcp.Message: raise ValueError(f'Incorrect type! {type(msgs[i][0])}')
        print(f'{i}) {msgs[i][0].header} | {msgs[i][1]}')

user_input = None
while True:
    show_options(all_msgs)
    user_input = input('> ')
    if user_input == 'q':
        exit(0)

    msg = all_msgs[int(user_input)][0]       # tcp.Message
    msg_type = all_msgs[int(user_input)][1]  # 0 = msg | 1 = request

    if msg_type == 0:
        client.send_message(msg)
        print('sending msg type')
        continue

    print(msg.header)
    resp = client.send_request(msg, timeout=10)
    if resp:
        print(f'Received response: {resp}')
    else:
        print('Sent ERROR')
