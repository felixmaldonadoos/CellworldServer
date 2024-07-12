import tcp_messages as tcp
import cellworld as cw

client = tcp.MessageClient()
client.connect(ip="172.26.176.129", port=4790)

def myprint(msg):
    print(msg)

print("sending pause")
client.send_message(tcp.Message("pause"))
client.router.add_route("pause", myprint )

# client.pause()


def show_move(message):
    print(message)
    pass

client.router.add_route("predator_move",show_move)
client.subscribe()

print("done")
while True:
    pass