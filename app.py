# app.py
print("Starting app.py...")

from flask import Flask
print("Importing init_routes from routes...")
from routes import init_routes

print("Creating Flask app...")
app = Flask("categoriser")
print("Initializing routes...")
init_routes(app)

if __name__ == "__main__":
    print("Running Flask app...")
    app.run(debug=True)