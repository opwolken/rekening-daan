# app.py
print("Starting app.py...")

from flask import Flask
from flask_socketio import SocketIO
print("Importing init_routes from routes...")
from routes import init_routes

print("Creating Flask app...")
app = Flask("categoriser")
socketio = SocketIO(app)
print("Initializing routes...")
init_routes(app)

if __name__ == "__main__":
    print("Running Flask app...")
    socketio.run(app, debug=True)