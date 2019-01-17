from flask import Flask
from flask_login import LoginManager

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
import json


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

login = LoginManager(app)
login.login_view = 'login'

with open('client_secret.json') as f:
    client_secret_json = json.load(f)
    CLIENT_ID = client_secret_json['web']['client_id']

# image upload setup
images = UploadSet('images', IMAGES)
configure_uploads(app, images)
patch_request_class(app, 4 * 1024 * 1024)  # limits image's size


# here app is the package
# not the above app var
from app import models, login_routes, routes, api
