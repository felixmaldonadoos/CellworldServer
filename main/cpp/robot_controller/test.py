import tcp_messages as tcp
import cellworld as cw
client = tcp.MessageClient()
client.connect(ip="127.0.0.1", port=666)
# client.send_message( tcp.Message("reset"))
# client.send_message(tcp.Message("stop"))



client.send_message("move_mouse", )

def show_move(message):
    print(message)

client.router.add_route("predator_move",show_move)
client.subscribe()

while True:
    pass





