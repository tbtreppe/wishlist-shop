# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_wishlist_model.py

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Item, Wishlist

os.environ['DATABASE_URL'] = "postgresql:///wishlist-test"

from app import app


db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class WishlistModelTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        db.drop_all()
        db.create_all()

        self.username = "test1"
        u1 = User.signup("test1", "email1@email.com", "password", None, "tester", "testerlast")
        u1.username = self.username
        u2 = User.signup("test2", "email2@email.com", "password", None, "tester2", "testerlast2")

        db.session.commit()


        self.u1 = u1

        self.u2 = u2

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_wishlist_model(self):
        w1 = Wishlist(name = "Fashion", username=self.username)
        db.session.add(w1)
        db.session.commit()

        self.assertEqual(len(self.u1.wishlist), 1)
