import tcp_messages as tcp
import cellworld as cw
<<<<<<< HEAD
client = tcp.MessageClient()
client.connect(ip="127.0.0.1", port=666)
# client.send_message( tcp.Message("reset"))
# client.send_message(tcp.Message("stop"))



client.send_message("move_mouse", )

def show_move(message):
    print(message)
=======

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
>>>>>>> fixing

client.router.add_route("predator_move",show_move)
client.subscribe()

<<<<<<< HEAD
while True:
    pass





=======
print("done")
while True:
    pass
>>>>>>> fixing
