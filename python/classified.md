# Process to convert main.py (BotEvade Server) into a class/library


## Tasks

### Create Generic server inherited from tcp.MessageServer

Requirements: 

- Receives message from routes shown below, only print out "received message: XXX " 
```
server.router.add_route("reset", reset)
server.router.add_route("prey_step", move_mouse)
server.router.add_route("stop", _stop_)
server.router.add_route("pause", _pause_)
server.router.add_route("close", _close_)
server.router.add_route("get_cell_locations", get_cell_locations) # ret json_cpp.JsonList
server.router.add_route("get_occlusions", get_occlusions)
```

- if you can, convert messages to requests from main.py

start and stop experiment, set up all routes like get cell locations and print out cell locations
either cell loc or occlusoins will print index or lists-- figure out which is which

reset = start
if get captures stop
restart again and loop

2/20-- 
- Test all messages and if they are properly routed. 
- Add any other routes if they're missing from main.py (and add them to client)
- Maybe after I add all my routes I can try turning my while True to a function that does it automatically:
- manually send messages vs automatically send messages
