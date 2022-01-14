from flask import Flask, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Item, Wishlist
from forms import UserAddForm, UserEditForm, LoginForm, WishlistForm
from sqlalchemy.exc import IntegrityError

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
    return render_template('home.html')

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
        return redirct(f"/users/{session['username']}")
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
        
            flash(f"Hello, {user.first_name}!", "success")
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

@app.route('/users/<username>', methods=['GET', 'POST'])
def show_user_details(username):
    if "username" not in session:
        flash("Please log in first!", 'error')
        return redirect("users/register")
    user = User.query.get(username)
    form = WishlistForm()
    return render_template("users/user_details.html", user=user, form=form)

@app.route('/users/<username>/newwishlist', methods=["GET", "POST"])
def add_wishlist():
    """Add a wish list."""
    if "username" in session:
        return redirct(f"/users/{session['username']}")
    
    form = WishlistForm()

    if form.validate_on_submit():
        wishlist = Wishlist(name=name)
        return redirect('/wishlist')
            
    return render_template('users/newwishlist.html', form=form)

    @app.route('/users/<username>/showwishlist', methods=['GET', 'POST'])
    def show_wishlist(wishlist):
        """Show a the users created wish list page and 
        have a search bar to search for and add images"""
        if "username" in session:
            return redirct(f"/users/{session['username']}")

        wishlist = Wishlist.query.get(wishlist)
        return render_template("/users/wishlist_details.html", wishlist=wishlist)
