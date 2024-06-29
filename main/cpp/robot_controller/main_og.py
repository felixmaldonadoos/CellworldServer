import cellworld as cw
import cellworld_game as game
import tcp_messages as tcp

data = {"prey":[], "predator":[]}

PORT = 4970 

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
    # predator_step.rotation = model.predator.state.direction
    server.broadcast_subscribed(message=tcp.Message("predato_step", body=predator_step))

