from flask import Flask, redirect, render_template, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Item, Wishlist
from forms import UserAddForm, UserEditForm, LoginForm, WishlistForm, SearchItemForm
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

"""logout user"""
@app.route('/logout')
def logout():
    session.pop('username')
    flash("Successfully logged out", 'success')
    return redirect ('/login')

"""edit and update user information"""
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
            flash("Updated information!", 'success')
            return redirect(f"/users/{user.username}")
        flash("Wrong password, please try again", 'danger')
    
    return render_template("users/edit.html", form=form, user=user)

"""go to user page and create a wishlist"""
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
            wishlist = Wishlist(name=name, user=user)
            db.session.add(wishlist)
            db.session.commit()
            flash(f"{wishlist.name} Wish List created!", "success")
            return redirect(f"/users/{wishlist.id}/wishlist_details")
            
    return render_template('users/user_details.html', form=form, user=user)

"""go to wishlist page and click search to go to search page"""
@app.route('/users/<int:wishlist_id>/wishlist_details', methods=['GET', 'POST'])
def wishlist_details(wishlist_id):
    if "username" not in session:
        flash("Please log in first!", 'error')
        return redirect("users/signup")
    
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    return render_template('users/wishlist_details.html',  wishlist=wishlist)


@app.route('/users/<int:wishlist_id>/search', methods=['GET', 'POST'])
def search():
    form = SearchItemForm()
    if form.validate_on_submit():
        name = form.name.data
        
        headers = {"apikey": "2797b24d-1fef-4568-89ac-45423bf372d6"}
        query = {"q": form.name.data,
        "hl": "en"}

        url = f"https://api.goog.io/v1/images/" + urllib.parse.urlencode(query)

        resp = requests.get(url, headers=headers)
        result = resp.json()
        print(result)
<<<<<<< HEAD
        return redirect("show_search_results")
        
    return render_template('users/search.html', form=form)

@app.route('/users/<int:item_id>/show_search_results')
def show_results():
    item = Item.query.get_or_404(item_id)
    return render_template('/users/show_search_Results')
=======
        session["result"] = result
        # pass result through session
       
        return redirect("/users/1/show_search_results")
        
    return render_template('users/search.html', form=form)

@app.route('/users/<int:wishlist_id>/show_search_results')
def show_results(wishlist_id):
    result = session["result"]
    return render_template('/users/show_search_results.html', result=result)
>>>>>>> baffc364f610ac0e8d0445d262ce3b6ddf252493

"""Delete wish list"""
@app.route('/users/<int:wishlist_id>/delete', methods=['POST'])
def delete_user(wishlist_id):
    if "username" not in session:
        flash("Please login first", 'error')
        return redirect("users/signup")
    wishlist = Wishlist.query.get(wishlist_id)
    db.session.delete(wishlist)
    db.session.commit()
    flash("Wishlist deleted!", "success")
    return redirect("/")


#@app.route('/users/search', methods=['POST'])
#def search():
 #   item = Item(
  #      name = request.json["name"],
   #     price = request.json["price"])
    
    #db.session.add(item)
    #db.session.commit()

    #return (jsonify(item=item.serialize()), 201)