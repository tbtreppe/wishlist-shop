#run python seed.py in terminal

from models import db, connect_db, User, Wishlist
from app import app

db.drop_all()
db.create_all()

u1 = User(username="AnnaM", email="annam@gmail.com", first_name="Anna", last_name="Mac", password="annam1234")
u2 = User(username="JohnS", email="johns@gmail.com", first_name="John", last_name="Smith", password="johns1234")

w1 = Wishlist(name="Clothing", username="AnnaM")
w2 = Wishlist(name="Travel", username="JohnS")

db.session.add(u1)
db.session.add(u2)
db.session.commit()
db.session.add(w1)
db.session.add(w2)
db.session.commit()
