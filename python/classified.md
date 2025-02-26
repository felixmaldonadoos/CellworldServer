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

2/20-- 
- Test all messages and if they are properly routed. -- Done
- Add any other routes if they're missing from main.py (and add them to client) -- Done for now... I think
- Maybe after I add all my routes I can try turning my while True to a function that does it automatically-- Haven't done yet
- manually send messages vs automatically send messages-- Also haven't done yet

2/26-- 
- change my laptop IP address and make it a static IP address while connected to eduroam
  - tip: use ping-- command but more of a action-- how to ping a port
- Current issues: I can't reset more than once (manually)
  - Figure out why this issue is happening
  - Fix it.
  - Try to do it so messages are automatically sent
- By friday I want my computer running experiments so current issues don't need to be fixed just yet, can be a 
- last minute thing to fix tomorrow night before friday experiments



