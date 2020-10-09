#!/usr/bin/env python3
"""  main standalone """
import sys
from app import app, cfg, db

if cfg.get("server") is None:
    print("Please config the port")
    sys.exit(0)
port = cfg['server'].get("port")
listen = cfg['server'].get("host")
if listen is not None:
    listen = listen.decode()
development = cfg['server'].get("debug")
if __name__ == '__main__':
    db.create_all()
    app.run(host=listen, port=port, debug=development)
