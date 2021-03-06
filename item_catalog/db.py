import os

from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from app import db
from app.models import User, Category, Item
from pathlib import Path
import shutil
from whoosh.fields import TEXT, ID, STORED, Schema
from whoosh.index import create_in
import json
import config


def drop_db():
    DB_URL = config.Config.SQLALCHEMY_DATABASE_URI
    print(DB_URL)

    if database_exists(DB_URL):
        print('Deleting database.')
        drop_database(DB_URL)
    
    if not database_exists(DB_URL):
        print('Creating database.')
        create_database(DB_URL)


def check_type(type_str, dct):
    return '__type__' in dct and dct['__type__'] == type_str


def user_from_dict(dct):
    user = User(
        username=dct['username'],
        email=dct['email']
    )
    user.set_password(dct['password'])

    return user


def category_from_dict(dct):
    return Category(name=dct['name'])


def item_from_dict(dct):
    try:
        category = Category.query.filter_by(name=dct['category']).one()

    except NoResultFound | MultipleResultsFound:
        print("{} category doesn't exist".format(dct['category']))
        return None

    user = User.from_email(dct['user_email'])

    if not user:
        return None

    return Item(
        name=dct['name'],
        description=dct['description'],
        category=category,
        category_id=category.id,
        user_id=user.id
    )


def make_decode_model(model_name, dict_to_model):
    def decode_model(dct):
        if check_type(model_name, dct):
            return dict_to_model(dct)
        else:
            return dct

    return decode_model


def load_init_data():
    model_load_instructions = [
        ('users', make_decode_model('User', user_from_dict)),
        ('categories', make_decode_model('Category', category_from_dict)),
        ('items', make_decode_model('Item', item_from_dict))
    ]

    for filename, model_decoder in model_load_instructions:
        path = "data/{}.json".format(filename)

        with open(path, 'r') as f:
            models_json = json.load(f, object_hook=model_decoder)

            for model in models_json:
                if model:
                    db.session.add(model)

            db.session.commit()


def init_whoosh():
    if os.path.exists('index'):
        shutil.rmtree('index')

    os.mkdir('index')

    schema = Schema(id=ID(stored=True, unique=True), name=TEXT)
    ix = create_in('index', schema=schema)

    return ix


def index_items(ix):
    items = Item.query.all()
    writer = ix.writer()

    for item in items:
        writer.add_document(
            id=str(item.id), name=item.name
        )

    writer.commit()


if __name__ == '__main__':
    drop_db()
    db.create_all()
    load_init_data()

    ix = init_whoosh()
    index_items(ix)
