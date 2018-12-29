from flask import Flask

app = Flask(__name__)

# here app is the package
# not the above app var
from app import routes