from flask_bcrypt import Bcrypt 
from flask_sqlalchemy import SQLAlchemy

bcrypt=Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """Users"""
    __tablename__="users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
    )

    email = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
    )

    first_name = db.Column(
        db.String(20),
        nullable=False,
    )

    last_name = db.Column(
        db.String(20),
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    wishlist_id = db.Column(
        db.Integer,
        db.ForeignKey('wishlist.id', ondelete='CASCADE'),
        nullable=False
    )

    @classmethod
    def signup(cls, username, email, password, image_url, first_name, last_name):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            first_name=first_name,
            last_name=last_name
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Item(db.Model):
    """Items"""
    __tablename__="items"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    price = db.Column(
        db.Float,
        nullable=False,
    )

    wishlist = db.relationship('Wishlist', backref="items")

class Wishlist(db.Model):
    """Wishlist"""
    __tablename__="wishlist"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )
    
    item_id = db.Column(
        db.Integer,
        db.ForeignKey('items.id', ondelete='CASCADE'),
        nullable=False)

    user = db.relationship('User', backref="wishlist")

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)