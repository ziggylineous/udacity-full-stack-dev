from app import db
from sqlalchemy import event
from app.models import Item
from whoosh.qparser import QueryParser
import os
from whoosh.index import open_dir

# this was taken from miguel grinberg's flask mega tutorial
def save_item_changes(session):
    print('save_item_changes')
    session._changes = {
        'add': [obj for obj in session.new if isinstance(obj, Item)],
        'update': [obj for obj in session.dirty if isinstance(obj, Item)],
        'delete': [obj for obj in session.deleted if isinstance(obj, Item)],
    }


def save_items_in_index(session):
    writer = ix.writer()
    with ix.searcher() as searcher:

        for obj in session._changes['add']:
            writer.add_document(name=obj.name, id=str(obj.id))

        for obj in session._changes['update']:
            writer.update_document(name=obj.name, id=str(obj.id))

        for obj in session._changes['delete']:
            doc_num = searcher.document_number(id=str(obj.id))

            if doc_num:
                print("found item {} - {}".format(obj.id, obj.name))
                writer.delete_document()
            else:
                print("DIDNT FOUND!!! item {} - {}".format(obj.id, obj.name))
                writer.delete_document()

        writer.commit()

    session._changes = None


def search_item(words):
    parser = QueryParser("name", schema=ix.schema)

    wildcard_words = ['*' + word + '*' for word in words]
    query_str = " OR ".join(wildcard_words)
    query = parser.parse(query_str)

    with ix.searcher() as searcher:
        results = searcher.search(query)

        # pair ids with db objects
        ids_ranks = {
            int(result.get('id')): result.rank
            for result in results
        }

        items = Item.query.filter(Item.id.in_(ids_ranks.keys())).all()

        return sorted(items, key=lambda item: ids_ranks[item.id])

    return []


print("initializing index")

if os.path.exists('index'):
    ix = open_dir('index')
else:
    ix = None

event.listen(db.session, 'before_commit', save_item_changes)
event.listen(db.session, 'after_commit', save_items_in_index)

print("index ready")

