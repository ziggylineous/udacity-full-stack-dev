from app import db, images

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    @classmethod
    def from_email(cls, email):
        return cls.query.filter_by(email=email).first()


    @staticmethod
    def create_and_save(username, email, password=''):
        new_user = User(
            username=username,
            email=email,
            password_hash='todo'
        )

        db.session.add(new_user)
        db.session.commit()

        return new_user

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    description = db.Column(db.String())
    image = db.Column(db.String())
    
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id'),
        nullable=False
    )
    category = db.relationship(
        'Category',
        backref=db.backref('items', lazy=True)
    )

    def __repr__(self):
        return '<Item {}>'.format(self.name)
    
    @property
    def image_url(self):
        filename = self.image if self.image else 'item_placeholder.png'
        return images.url(filename)


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<Category {}>'.format(self.name)