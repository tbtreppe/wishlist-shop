from flask import Flask, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Item, Wishlist
from forms import UserAddForm, UserEditForm, LoginForm, WishlistForm
from sqlalchemy.exc import IntegrityError
from secret_key import API_SECRET_KEY
import urllib
import requests

API_BASE_URL = "https://api.goog.io/v1/images/{query}"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///wishlist"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "SECRET!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()



"""Show homepage."""
@app.route('/')
def homepage():
    if "username" in session:
        wishlist = Wishlist.query.all()
#        wishlist_id = [w.id for w. username.wishlist] + [user.username]
        return render_template('home.html', wishlist=wishlist) #wishlist=wishlist
    else:
        return render_template('home_no_user.html')

"""Signup user"""
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    form = UserAddForm()

    if form.validate_on_submit():
        
        first_name=form.first_name.data
        last_name=form.last_name.data
        username=form.username.data
        password=form.password.data
        email=form.email.data
        image_url=form.image_url.data or User.image_url.default.arg
        user = User.signup(username, email, password, image_url, first_name, last_name)
        db.session.add(user)
        try:
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)
        if user:
            session['username'] = user.username
            flash ('Welcome!', 'success')

            return redirect(f"/users/{user.username}")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
        
            flash(f"Hello {user.first_name}!", "success")
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            flash("Invalid credentials.", 'danger')
            return render_template('users/login.html', form=form)

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('username')
    flash("Successfully logged out", 'success')
    return redirect ('/login')

@app.route('/users/<username>/update', methods=['GET', 'POST'])
def edit_profile(username):
    if "username" not in session:
        flash("Please log in first!", 'error')
        return redirect("users/signup")
    user = User.query.get(username)
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or "/static/images/default-pic.png"
            db.session.commit()
            
            return redirect(f"/users/{user.username}")
        flash("Wrong password, please try again", 'danger')
    
    return render_template("users/edit.html", form=form, user=user)

@app.route('/users/<username>', methods=['GET', 'POST'])
def show_user_details(username):
    if "username" not in session:
        flash("Please log in first!", 'error')
        return redirect("users/signup")
    user = User.query.get(username)
    if "wishlist_id" not in session:
        form = WishlistForm()
    
        if form.validate_on_submit():
            name = form.name.data
            wishlist = Wishlist(name=name)
            db.session.add(wishlist)
            db.session.commit()
            flash(f"{wishlist.name} Wish List created!", "success")
            return redirect(f"/users/{wishlist.id}/wishlist_details")
            
    return render_template('users/user_details.html', form=form, user=user)

@app.route('/users/<int:wishlist_id>/wishlist_details', methods=['GET'])
def add_items_to_wishlist(wishlist_id):
    if "username" not in session:
        flash("Please log in first!", 'error')
        return redirect("users/signup")
    
    wishlist = Wishlist.query.get_or_404(wishlist_id)

    return render_template('users/wishlist_details.html',  wishlist=wishlist)

@app.route('/users/search', methods=['POST'])
def search():
    url = f"https://api.goog.io/v1/images/" + urllib.parse.urlencode(query)

    resp = requests.get(url, API_SECRET_KEY=API_SECRET_KEY)
    result = json.loads(resp.text)
    return render_template('users/search_results.html', result=result)



#@app.route('/users/search', methods=['POST'])
#def search():
 #   item = Item(
  #      name = request.json["name"],
   #     price = request.json["price"])
    
    #db.session.add(item)
    #db.session.commit()

    #return (jsonify(item=item.serialize()), 201)