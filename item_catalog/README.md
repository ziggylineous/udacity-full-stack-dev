# Item Catalog

This proyect consists in an item browser. Each item has a category,
so you can also browse items selecting a category.

The main features are:

- item CRUD
- user authorization and authentication. Create, Update and Delete features are available only for logged in users
- user authentication with google's oauth api
- Item image uploading (saved in the servers filesystem)
- An API endpoint to search for items. This was implemented with
a python's whoosh index (so you do not have to install anything) 


## Setup
1. Install posgresql. Create a psql user `admin` with password `dbpw` with createdb permission. Otherwise, create whatever user you want and export it as `ITEM_CATALOG_DB_USER` and `ITEM_CATALOG_DB_PASSWORD`, in order to connect to the db.
2. Create a [python 3 environment](https://docs.python-guide.org/dev/virtualenvs/), activate that environment and install with pip:
    - flask
    - psycopg2 (posgresql)
    - flask-sqlalchemy (simplifies queries, creates a scoped_session)
    - sqlalchemy-utils
    - flask-wtf (form validation)
    - flask-uploads
    - oauth2client
    - requests
    - whoosh (full text search in the api requirement)
You can install all running  `pip install -r requirements.txt`.
3. Set the `FLASK_APP` environment variable to `item_catalog.py`.
   In Linux or MacOS you can do this with `export FLASK_APP=item_catalog.py`. You can run it in debug mode by setting `FLASK_ENV=development`.
4. Standing at item_catalog, run `python db.py` to create the database and load some starting models.
   This also creates the whoosh index for searching items.


## Running
In the terminal, navigate to item_catalog directory and run: `flask run`.
If you need it to run the server in a particular port, type `flask run --port <PORT_NUMBER>`. In Vagrant you may need to run it on the 0.0.0.0 address to access from the host computer: to achieve this, pass the `--host 0.0.0.0` option to the previous command.


(In the virtual machine of the FSND, you have also to export:
- `export LC_ALL=C.UTF-8`
- `export LANG=C.UTF-8`)

   
## Authentication
The `python db.py` step creates 2 users also, that you can use to login:
   - username: Pepe, password: 12345
   - Super, 54321

Besides, you can authenticate with a google account


## search API
The api endpoint searches an item given several terms. The path is:

`/api/item`

it takes one query param `q`, which stands for the search terms
for the item you want to find. Each of these words has to be separated by a comma.
For example:

```
/api/item?q=word1,word2,word3
```

The words sent don't need to be an exact match of the item name.
They can be a part of it.

#### Implementation
This search is implemented with `whoosh`, which is a content search library
that is fully implemented in python. It creates a index with a schema where you
specify which fields should be searchable.  
