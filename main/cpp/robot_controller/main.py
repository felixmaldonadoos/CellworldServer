import cellworld as cw
import cellworld_game as game
import tcp_messages as tcp


# todo:
# 1. create route for cpp server to send predator data to python server
# 2. add thread to clear data and send to cpp server for storage. if data empty, wait for data to be filled 

data_buffer = {"prey":[], "predator":[]}

PORT = 4790 

loader = game.CellWorldLoader(world_name="21_05")
model = game.BotEvade(world_name="21_05",
                      render=True,
                      time_step=.025)
model.prey.dynamics.turn_speed = 0
model.prey.dynamics.forward_speed = 0
model.reset()

server = tcp.MessageServer()

def move_mouse(message: tcp.Message):
    step: cw.Step = message.get_body(body_type=cw.Step)
    model.prey.state.location = (step.location.x, step.location.y)

def get_predator_step(message):
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    return predator_step

def reset(message):
    model.reset()

running = True

def stop(message):
    global running
    running = False

server.router.add_route("reset", reset)
server.router.add_route("prey_step", move_mouse)
server.router.add_route("get_predator_step", move_mouse)
server.router.add_route("stop", stop)

server.allow_subscription = True
server.start(PORT)

# model.view.add_event_handler("mouse_move", move_mouse)
while running:
    model.step()
    predator_step = cw.Step(agent_name="predator")
    predator_step.location = cw.Location(*model.predator.state.location)
    predator_step.rotation = model.predator.state.direction
    server.broadcast_subscribed(message=tcp.Message("predator_step", body=predator_step))

