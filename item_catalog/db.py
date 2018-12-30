from app import db
from sys import argv
import os


if __name__ == '__main__':
    arg_count = len(argv)

    if arg_count == 1:
        db.create_all()
    else:
        action = argv[1]
        
        if action == 'create':
            db.create_all()
        elif action == 'drop':
            db.drop_all()
            os.remove('item_catalog.db')
        else:
            print('unknown action {}'.format(action))
        