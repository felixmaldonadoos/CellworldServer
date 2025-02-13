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

if client.send_message(tcp.Message(header='start', body='')):
    print("Sent reset OK")

i = 0
t0 = time.time()
print('== starting main loop ==')

for i in range(1000):
    tnow = time.time() - t0
    x,y = 0.5,0.5
    msg = tcp.Message(header="prey_step", body=cw.Step(location=cw.Location(x, y), time_stamp=tnow, frame=i))  # 0,1
    client.send_message(msg)
    print(f'frame sent: {i}')
    time.sleep(0.2)

    if i % 100 == 0:
        print(f'requesting cell location')
        client.send_message(tcp.Message(header="get_cell_location", body=cw.Step(location=cw.Location(x, y), time_stamp=tnow, frame=i)))

        print("Requesting cell location")
        client.send_message(tcp.Message(header="get_occlusions", body=cw.Step(location=cw.Location(x, y), time_stamp=tnow, frame=i)))

    if i % 200 == 0:
        print("Testing reset")
        client.send_message(tcp.Message(header="reset", body=''))


print("done")

# def test_unrouted():
#     # create client
#     # connect
#     # send message to unroated route (i.e. did not do server.router.addroute("header")
#     return None
#
# def test_request():
#
#     # request = a message where the serverside callback returns a string
