# the first app is the package,
# the second is the Flask application
from app import app

@app.route('/')
@app.route('/index')
@app.route('/items')
def home():
    return 'test ok!'