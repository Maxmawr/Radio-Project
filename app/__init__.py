from flask import Flask

app = Flask(__name__)

from app import routes

if __name__ == 'app':
    app.run(debug=True)
