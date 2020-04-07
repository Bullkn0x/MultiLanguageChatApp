#!/bin/env python
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    print('Server started on port 8000')
    socketio.run(app,log_output=False, port=8000)
