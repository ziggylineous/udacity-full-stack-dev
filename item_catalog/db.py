from app import db
from app.models import Category
from pathlib import Path
import json

def drop_db():
    path = Path('item_catalog.db')

    if path.exists() and path.is_file():
        db.drop_all()
        path.unlink()
        print('dropped db')


def decode_category(dct):
    if '__type__' in dct and dct['__type__'] == 'Category':
        return Category(name=dct['name'])
    
    return dct


def load_categories():
    categories_file = open('data/categories.json', 'r')
    categories_json = json.load(categories_file, object_hook=decode_category)

    for cat in categories_json:
        db.session.add(cat)
    
    db.session.commit()


if __name__ == '__main__':
    drop_db()
    db.create_all()
    load_categories()
        