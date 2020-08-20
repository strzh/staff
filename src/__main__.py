from staff import *
from db import *

redis=connect()
port=redis.hget("webgui","port")
listen=redis.hget("webgui","listen")
if not listen is None:
    listen=listen.decode()
development=redis.get("developmentmode")
app.run(host=listen,port=port,debug=development)
