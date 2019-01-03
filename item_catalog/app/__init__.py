from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# image upload setup
images = UploadSet('images', IMAGES)
configure_uploads(app, images)
patch_request_class(app, 4 * 1024 * 1024) # limits image's size

# here app is the package
# not the above app var
from app import routes, models