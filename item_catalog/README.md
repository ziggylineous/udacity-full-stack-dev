# Item Catalog

## Setup
1. Create a python 3 environment and install with pip:
    - flask
    - flask-sqlalchemy (simplifies queries, creates a scoped_session)
    - flask-wtf (form validation)
    - flask-uploads
    - oauth2client
    - requests
    - whoosh (full text search in the api requirement)
    
You can install all running  `pip install -r requirements.txt`.
2. Set the `FLASK_APP` environment variable to `item_catalog.py`
3. Standing at item_catalog, run `python db.py` to create the database and load some starting models

## Running
In the terminal, navigate to item_catalog directory and run: `flask run`