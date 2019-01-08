from app import db
from app.models import User, Category, Item
from pathlib import Path
import json

def drop_db():
    path = Path('item_catalog.db')

    if path.exists() and path.is_file():
        db.drop_all()
        path.unlink()
        print('dropped db')


def decode_models(dct):
    if '__type__' in dct:
        if dct['__type__'] == 'Category':
            return Category(name=dct['name'])

        if dct['__type__'] == 'User':
            user = User(
                username=dct['username'],
                email=dct['email']
            )
            user.set_password(dct['password'])
            return user

    return dct



def load_init_data():
    initial_models_file = open('data/db_init_data.json', 'r')
    models_json = json.load(
        initial_models_file,
        object_hook=decode_models
    )

    for user in models_json['users']:
        db.session.add(user)

    for cat in models_json['categories']:
        db.session.add(cat)

    
    db.session.commit()


if __name__ == '__main__':
    drop_db()
    db.create_all()
    load_init_data()
