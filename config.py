from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask_socketio import SocketIO

app = Flask(__name__)

# Secret key for Flask sessions
app.secret_key = b'\xc2A\x1c\xc6\xc5QvJ?ZH$\x13\\4\xb0'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT configuration
app.config['JWT_SECRET_KEY'] = 'ce81d8454bd966ba09bbbdf723f632fd'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=168)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-Bcrypt
bcrypt = Bcrypt(app)

# Initialize JWT
jwt = JWTManager(app)

# Enable CORS
CORS(app)
api = Api(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Define your models and APIs here (e.g., User, Message)

# Example of a Flask route
@app.route('/')
def index():
    return 'Hello, World!'

# Example of SocketIO event handler
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Run the Flask application with SocketIO
if __name__ == '__main__':
    socketio.run(app, port=5555, debug=True)
