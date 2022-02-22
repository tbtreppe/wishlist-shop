from flask import Flask, redirect, render_template, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Item, Wishlist
from forms import UserAddForm, UserEditForm, LoginForm, WishlistForm, SearchItemForm, AddItemForm
from sqlalchemy.exc import IntegrityError
#from secret_key import API_SECRET_KEY
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
#       wishlist_id = [w.id for w. username.wishlist] + [user.username]
        return render_template('home.html', wishlist=wishlist)
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

"""go to wishlist page and enter item to search for"""
@app.route('/users/<int:wishlist_id>/wishlist_details', methods=['GET', 'POST'])
def wishlist_details(wishlist_id):
    if "username" not in session:
        flash("Please log in first!", 'error')
        return redirect("users/signup")
    
    wishlist = Wishlist.query.get_or_404(wishlist_id)

    if "item_id" not in session:
        form = SearchItemForm()
        if form.validate_on_submit():
            name = form.name.data
            item = Item(name=name)
            
            headers = {"apikey": "2797b24d-1fef-4568-89ac-45423bf372d6"}
            query = {"q": form.name.data,
            "hl": "en"}

            url = f"https://api.goog.io/v1/images/" + urllib.parse.urlencode(query)
            resp = requests.get(url, headers=headers)
            result = resp.json()
            print(result)
            fake_result = {'results': [], 'image_results': [{'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQzMkABKTqkpMNZ0ymicN2Y6RrZlLcOnckwqsh4MuJMmR-8FMv8unOwxKO4RWo&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://en.wikipedia.org/wiki/Tiger&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIARAC&usg=AOvVaw1uAwAyCFLLTSccolureJOn', 'title': 'Tiger - Wikipedia   en.wikipedia.org', 'domain': 'Tiger - Wikipedia   en.wikipedia.org'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQCigxKxFnE_xCi-Wd_e3Cu_FCXXNPnhR4847NA9YC50BY9vZd7Wqnpj28gaeY&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.worldwildlife.org/species/tiger&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIEBAC&usg=AOvVaw10qpmBiTYrUEqH126lBkKe', 'title': 'Tiger | Species | WWF   www.worldwildlife.org', 'domain': 'Tiger | Species | WWF   www.worldwildlife.org'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpjLeu9l8DApfPaIah65r5ftr1tmBH-JzptdU5o8EUpMpqOane3qdA8AkR4fY&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.nationalgeographic.com/animals/mammals/facts/sumatran-tiger&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIERAC&usg=AOvVaw2rFBX2lW4MFC0pJuzFgCYC', 'title': 'Sumatran tiger, facts and...   www.nationalgeographic.com', 'domain': 'Sumatran tiger, facts and...   www.nationalgeographic.com'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRwcAILyeiSWwDiQIprqFBvE9pHXt4XgagAKcPS-4T6F_U_cIiBS2J8kCkLFQ&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.britannica.com/animal/tiger&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIDxAC&usg=AOvVaw1YfULc50KDmq_rvY5s5QlY', 'title': 'tiger | Facts, Information,...   www.britannica.com', 'domain': 'tiger | Facts, Information,...   www.britannica.com'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRv2qzy6_c_zurQx4NcHhN8bNf3_qe81rIulCRnJRCVGrmaMKKTc8iOh_h0A6o&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.worldwildlife.org/species/sunda-tiger&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIExAC&usg=AOvVaw0EjciyUcDxapgqvfJ8hZsJ', 'title': 'Sunda Tiger | Species | WWF...   www.worldwildlife.org', 'domain': 'Sunda Tiger | Species | WWF...   www.worldwildlife.org'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRRfrptazgMiw5Gp8iZRdYEsnelrFGT767BZYd3dv6eOOJuc9Z7NLzycBDUMQ&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://en.wikipedia.org/wiki/Bengal_tiger&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIEhAC&usg=AOvVaw2SGsLtLb11sONUnjcRm_X9', 'title': 'Bengal tiger - Wikipedia   en.wikipedia.org', 'domain': 'Bengal tiger - Wikipedia   en.wikipedia.org'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRlQXOJkIh5n6FSADudACkVqJn7PIWlQkddF3TRHQxfqrYod-_PmeMJXUkgbw&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.livescience.com/27441-tigers.html&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIDhAC&usg=AOvVaw36E3SY2-E_HDqf6ONnymfp', 'title': 'Tigers: The Largest Cats in...   www.livescience.com', 'domain': 'Tigers: The Largest Cats in...   www.livescience.com'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTqam8cnK5vinIZJ2nhoR8-VCNO9gd9iIanofHcVY38UVMd2FAIoMQ64f4TdhE&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.bbc.co.uk/news/world-asia-57308587&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQICRAC&usg=AOvVaw2Ce8uEWc_d34J7ZvO25Q12', 'title': 'Bangladesh arrests tiger...   www.bbc.co.uk', 'domain': 'Bangladesh arrests tiger...   www.bbc.co.uk'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBoQ75zDELO3qnAzhfCMFNxerEAq9a4jJAC4QUkjDVxvF8XYKNAvpQLj9YRV4&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.britannica.com/animal/tiger&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQICxAC&usg=AOvVaw1e3eXIxsqiPukGfs6fm9bW', 'title': 'tiger | Facts, Information,...   www.britannica.com', 'domain': 'tiger | Facts, Information,...   www.britannica.com'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTZ5fDjo8iCKTYJgxIynGGqQrH8XD6piaCKdJp5gSlDajEOd3usQ7wdH62Z6Q&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.tierart.de/en-us/interesting-facts/about-tigers-panthera-tigris&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQICBAC&usg=AOvVaw3iZ99STta7tRXpJaEGdScN', 'title': 'Interesting facts about...   www.tierart.de', 'domain': 'Interesting facts about...   www.tierart.de'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEP78TjdxZS99_eMcTn9v_Q_KToEzsfBmLrDKTuUHsfzemHyJLlbXQtx_H1w&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.bbc.com/news/world-us-canada-59826100&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIChAC&usg=AOvVaw0ku9JcgYx5ISLPos2J1hPC', 'title': 'Tiger shot and dies at...   www.bbc.com', 'domain': 'Tiger shot and dies at...   www.bbc.com'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6jGTsvNUaX1XooBzZWh5uRq_EqhXm7CsKHfQNmuEU2SqiiZRFhEzfu5-R_f0&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://a-z-animals.com/animals/tiger/&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIBxAC&usg=AOvVaw0qbBufYVXCRj8zqVPtwsUz', 'title': 'Tiger Animal Facts |...   a-z-animals.com', 'domain': 'Tiger Animal Facts |...   a-z-animals.com'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_mxwwcKjILG89nACr1eMpkm00SBEhj1lCtyEZHzbpVeiqqeop8vzjnWxMcw&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://nationalzoo.si.edu/animals/tiger&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIDBAC&usg=AOvVaw06sB3f0QYfxW72oIdD-iK6', 'title': "Tiger | Smithsonian's...   nationalzoo.si.edu", 'domain': "Tiger | Smithsonian's...   nationalzoo.si.edu"}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRCXFU5TCwdwpqJXvBk7ZHr0FIt5fg3fAttdVhZ-iUqPNKmr5PaGMqsPrgnlg&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.theguardian.com/us-news/2021/dec/30/tiger-fatally-shot-florida-naples-zoo&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIDRAC&usg=AOvVaw3HIteLatkB9u3s93bObxNa', 'title': 'Critically endangered tiger...   www.theguardian.com', 'domain': 'Critically endangered tiger...   www.theguardian.com'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT6ca9iMKOQdqE5b8aX2zUyjqW-mubnalMiGgw_U9baSk9JSVKV6FBNd7xMzQ&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.theverge.com/2020/4/3/21203686/tiger-king-netflix-meme-tiktok-twitter-live-tv-coronavirus-viral&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIAhAC&usg=AOvVaw1rmPZK5Lnt0xmdn5g90JAk', 'title': 'Tiger King is a viral...   www.theverge.com', 'domain': 'Tiger King is a viral...   www.theverge.com'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6Ng7ULXlTLJ4qQycR5XjvVdU_aGtfI0JHZEWogWH8wnE4G7I1lXmWVR9Z3GE&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.theguardian.com/world/2019/jul/29/india-wild-tiger-population-rises-conservation&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIBRAC&usg=AOvVaw0YCCU17bON5ems1j1a3ozQ', 'title': "India's wild tiger...   www.theguardian.com", 'domain': "India's wild tiger...   www.theguardian.com"}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxqaWJy7miq3iZjAfu6MHfitJWCdQuYGeu28RK0aM8MnJSb76WB2XxccZ4eGk&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.independent.co.uk/news/world/russia-logger-siberian-amur-tiger-b1907985.html&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIBBAC&usg=AOvVaw24GnHs7ikNSUDTUwaEH4-i', 'title': "Tiger 'eats logger who went...   www.independent.co.uk", 'domain': "Tiger 'eats logger who went...   www.independent.co.uk"}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQoMMYP2gdBWRmY1-bwSsdJqbaFbyOspBJZjBOgDhJ17TGG2TtT68cmESl4Opo&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.nhm.ac.uk/wpy/gallery/2020-tiger-tiger-burning-out&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIBhAC&usg=AOvVaw0ySrJi22dkItgPuMQXAM-X', 'title': 'Tiger Tiger, Burning Out |...   www.nhm.ac.uk', 'domain': 'Tiger Tiger, Burning Out |...   www.nhm.ac.uk'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT5byDW9J_aPgHTGzO-S3v25Hde51WAgKSsJbc-xeqLPh664tVOqlGMBdG-2g&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://en.wikipedia.org/wiki/White_tiger&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIAxAC&usg=AOvVaw0Gg0mvhsqfMO_E4GHI0Vco', 'title': 'White tiger - Wikipedia   en.wikipedia.org', 'domain': 'White tiger - Wikipedia   en.wikipedia.org'}}, {'image': {'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBuywfXRrHWRCgBYt7OaAb3qvVfyUT4UZjCccEmQV5rzeCbFZ4pjLwCW2Isg&s', 'alt': ''}, 'link': {'href': 'https://www.google.com/url?q=https://www.insider.com/zookeeper-mauled-death-by-tiger-after-electric-fence-turned-off-2021-6&sa=U&ved=2ahUKEwjIy-WxnpP2AhWq4YUKHRmNCLwQr4kDegQIABAC&usg=AOvVaw0Ob-i2CYoEP5VmyT_p_20O', 'title': "South Africa: 'Hormonally...   www.insider.com", 'domain': "South Africa: 'Hormonally...   www.insider.com"}}], 'total': None, 'answers': [], 'ts': 1.801138162612915, 'device_type': None}
            session["result"] = fake_result
            # pass result through session
       
            return redirect(f"/users/{wishlist.id}/show_search_results")
    return render_template('users/wishlist_details.html',  wishlist=wishlist, form=form)


"""Show search results and "like" button to add item to your wishlist """
@app.route('/users/<int:wishlist_id>/show_search_results', methods=['GET', 'POST'])
def show_results(wishlist_id):
    result = session["result"]
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    if "item_id" not in session:
        form = AddItemForm()
        
        if form.validate_on_submit():
            name = form.name.data
            item = Item(name=name, wishlist_id=wishlist.id)
            db.session.add(item)
            db.session.commit()
            flash("Item added!", "success")
            return redirect(f"/users/{wishlist.id}/wishlist_details")  
    
    return render_template('/users/show_search_results.html', result=result, form=form, wishlist=wishlist)


"""
NOT ACCESSED
"""
@app.route('/users/<int:wishlist_id>/wishlist_details', methods=["GET", "POST"])
def show_likes(item_id):
    if "username" not in session:
        flash("Please login first", 'error')
        return redirect("users/signup")
    item= Item.query.get_or_404(item_id)
    return render_template('users/wishlist_details.html', item=item)

# @app.route('/users/<int:item_id>/likes', methods=["POST"])
# def add_like(item_id):
#     if "username" not in session:
#         flash("Please login first", 'error')
#         return redirect("users/signup")
    
    # if "item_id" not in session:
    #     form = AddItemForm()
        
    #     if form.validate_on_submit():
    #         description = form.description.data
    #         item = Item(description=description)
    #         db.session.add(item)
    #         db.session.commit()
    #         flash("Item added!", "success")
    #         return redirect(f"/users/{item.id}/likes")
        # return render_template('users/likes.html', form=form)
       
    # liked_item = Item.query.get_or_404(item_id)
    # if liked_item.wishlist_id == username:
    #     return abort(403)
    
    # wishlist_likes = session['username']

    # if liked_item in wishlist_likes:
    #     wishlist_id.likes = [like for like in wishlist_likes if like != liked_item]
    # else:
    #     wishlist_likes.append(liked_item)

    # db.session.commit()

    # return redirect('/')

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
    return redirect('/')

