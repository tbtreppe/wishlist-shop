# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Item, Wishlist

os.environ['DATABASE_URL'] = "postgresql:///wishlist-test"

from app import app


db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None,
                                    first_name="tester",
                                    last_name="lasttester")
        self.testuser_username = "testuser"
        self.testuser_username = self.testuser_username                        

        self.u1 = User.signup("abc", "test1@test.com", "password", None, "tester1", "lasttester1")
        self.u1_username = "abc"
        self.u1_username = self.u1_username
        self.u2 = User.signup("efg", "test2@test.com", "password", None, "tester2", "lasttester2")
        self.u2_username = "efg"
        self.u2_username = self.u2_username
        self.u3 = User.signup("hij", "test3@test.com", "password", None, "tester3", "lasttester3")
        self.u4 = User.signup("testing", "test4@test.com", "password", None, "tester4", "lasttester4")

        db.session.commit()
    
    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_user_index(self):
        with self.client as c:
            resp= c.get("/users")
            self.assertIn("testuser", str(resp.data))
            self.assertIn("abc", str(resp.data))
            self.assertIn("efg", str(resp.data))
            self.assertIn("hij", str(resp.data))

    def test_user_show(self):
        with self.client as c:
            resp=c.get(f"/users/{self.testuser_username}")
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", str(resp.data))

    def setup_wishlist(self):
        wishlist1 = Wishlist(name="Clothing", username=self.testuser)
        wishlist2 = Wishlist(name="Travel", username=self.testuser)
        wishlist3 = Wishlist(id=7777, name="Sports", username=self.u1)
        
        db.session.add_all([wishlist1, wishlist2, wishlist3])
        db.session.commit()

    def add_wishlist(self):
        w = Wishlist(id= 1234, name="Home", username=self.u1)
        db.session.add(w)
        db.session.commit()

        with self.client as c:
            resp = c.post("/users/1234/wishlist_details", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

    def test_delete_wishlist(self):
        self.setup_wishlist()

        w = Wishlist.query.filter(Wishlist.name=="Sports").one()
        self.assertIsNotNone(w)
        self.assertNotEqual(w.wishlist_id, self.testwishlist_id)


    def test_unauthorized_wishlist_page_access(self):
        self.setup_wishlist()
        with self.client as c:

            resp = c.get(f"/users/{self.testwishlist_id}/wishlist_details")
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("abc", str(resp.data))
            self.assertIn("Please log in first!", str(resp.data))


