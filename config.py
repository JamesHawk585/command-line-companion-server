# config.py
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_session import Session

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# #This secret key has been pushed to GitHub. Generate a new secret key before deployment. 
app.secret_key = b'\xf5\xadOu\x94{\x05F\xf2/\xc2\xc1\xaa\x1a)%' # In the terminal, run: python -c 'import os; print(os.urandom(16))'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False


db = SQLAlchemy()
migrate = Migrate(app, db)
db.init_app(app)
ma = Marshmallow(app)

bcrypt = Bcrypt(app)

api = Api(app)

CORS(app)