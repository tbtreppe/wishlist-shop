# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_model.py

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Item, Wishlist

os.environ['DATABASE_URL'] = "postgresql:///wishlist-test"

from app import app


db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserModelTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None, "tester", "testerlast")

        u2 = User.signup("test2", "email2@email.com", "password", None, "tester2", "testerlast2")

        db.session.commit()


        self.u1 = u1

        self.u2 = u2

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            first_name="tester",
            last_name="testerlast",
        )

        db.session.add(u)
        db.session.commit()

        # User should have no wishlist
        self.assertEqual(len(u.wishlist), 0)

    def test_valid_signup(self):
        u_test = User.signup("testing", "emailtest@email.com", "password", None, "testingtest", "testingtestlast")

        db.session.commit()

        self.assertEqual(u_test.username, "testing")
        self.assertEqual(u_test.email, "emailtest@email.com")

    def test_fail_signup(self):
        invalid = User.signup(None, "emailtest@email.com", "password", None, "testingtest", "testingtestlast")
  
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_user_authenticate(self):
        u = User.authenticate(self.u1.username, "password")

        self.assertIsNotNone(u)

    def test_username_authenticate_invalid(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))

    

