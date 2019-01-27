import os

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-baparrucha-paw-patrol'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #    'sqlite:///' + os.path.join(base_dir, 'item_catalog.db')
    ITEM_CATALOG_DB_USER = os.environ.get('ITEM_CATALOG_DB_USER') or\
                            'catalog'
    ITEM_CATALOG_DB_PASSWORD = os.environ.get('ITEM_CATALOG_DB_PASSWORD') or\
                                'dbpw'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://'
    SQLALCHEMY_DATABASE_URI += "{}:{}".format(
                                    ITEM_CATALOG_DB_USER,
                                    ITEM_CATALOG_DB_PASSWORD
                                )
    SQLALCHEMY_DATABASE_URI += '@127.0.0.1/item_catalog'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_IMAGES_DEST = os.path.join(base_dir, 'images')