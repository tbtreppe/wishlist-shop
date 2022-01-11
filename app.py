from flask import Flask, redirect, render_template,flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Item, Wishlist
from forms import UserAddForm, UserEditForm, LoginForm, WishlistForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wishlist'
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
    if "user_id" in session:
        return redirect(f"/users/{session['user_id']}")
    form = UserAddForm()

    if form.validate_on_submit():
        
        user = User.signup(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            image_url=form.image_url.data or User.image_url.default.arg,
            )
        db.session.add(user)
        try:
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        session['user_id'] = user.user_id
        flash ('Welcome!', 'success')

        return redirect(f"/users/{user.user_id}")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    if "user_id" in session:
        return redirct(f"/users/{session['user_id']}")
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
        
            flash(f"Hello, {user.first_name}!", "success")
            session['user_id'] = user.user_id
            return redirect(f"/users/{user.user_id}")
        else:
            flash("Invalid credentials.", 'danger')
            return render_template('users/login.html', form=form)

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user_id')
    flash("Successfully logged out", 'success')
    return redirect ('/login')

@app.route("/users/<int:user_id>", methods=['GET', 'POST'])
def show_user_details(user_id):
    if "user_id" not in session:
        flash("Please log in first!", 'error')
        return redirect("users/register")
    user = User.query.get(user_id)
    return render_template("users/user_details.html", user=user)

@app.route('/users/<int:user_id>/newwishlist', methods=["GET", "POST"])
def add_wishlist():
    """Add a wish list."""
    if "user_id" in session:
        return redirct(f"/users/{session['user_id']}")
    
    form = WishlistForm()

    if form.validate_on_submit():
        wishlist = Wishlist(name=name)
        return redirect('/wishlist')
            
    return render_template('users/newwishlist.html', form=form)