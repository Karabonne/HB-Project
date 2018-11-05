"""server file for bot playground."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from datetime import date, datetime
from model import Bot, User, Post, Source, connect_to_db, db
from processing import get_tweets
from markov import make_chains, make_text

import json

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC123456hackbright"

# catches Jinja2 erorrs
app.jinja_env.undefined = StrictUndefined

# 1. INFO DISPLAY SECTION ---------------------------------

# @app.route('/')
# def show_index():
#     """TODO: Main page - shows a stream of bot posts."""

#     return render_template("homepage.html")


@app.route('/user/<user_id>')
def show_user_page(user_id):
    """TODO: Shows a user info page, including list of user's bots."""

    user = User.query.get(user_id)
    # If a user can have many bots, we should have a one to many relationship so we can just do this:

    return render_template("user.html",
                              user=user,
                              user_bots=user.bots)


@app.route('/bot/<bot_id>')
def show_bot_page(bot_id):
    """TODO: Shows a bot info page, including posts and creator."""

    bot = Bot.query.get(bot_id)
    
    return render_template("bot.html",
                            bot=bot,
                            creator=bot.user,
                            bot_posts=bot.posts)


@app.route('/')
def show_bot_directory():
    """Shows a bot directory."""

    bots = Bot.query.all()

    return render_template("directory.html", bots=bots)


# 2. USER REGISTRATION AND LOGIN SECTION ------------------


@app.route("/register", methods=["GET"])
def show_reg_form():
    """Displays a user registration form."""

    return render_template("registration.html")


@app.route("/register", methods=["POST"])
def process_reg():
    """Adds user to DB."""

    new_username = request.form.get('username')
    pswd = request.form.get('password')
    desc = request.form.get('description')
    icon = request.form.get('icon')

    # Check for user username in db
    db_username = User.query.filter(User.username == new_username).first()

    if not db_username:
        user = User(**request.form) # optional approach, but cleaner in this particular use-case
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
    else:
        flash('username address already exists - try again?')

    return redirect("/")


@app.route("/login", methods=["POST"])
def login_user():
    """Adds user information to session."""

    login_username = request.form.get('username')
    pswd = request.form.get('password')

    user = User.query.filter(User.username == login_username).first()


    if user:
        if user.password == pswd:
            # add user info to Flask session
            session['user_id'] = user.user_id
            session['username'] = user.username
            flash('Successfully logged in!')
            return redirect("/")
        else:
            flash('Invalid password!')
    else:
        flash('User not found!')

    return redirect("/")


@app.route("/logout")
def log_out():
    """Logs user out of session."""

    session.clear()

    return redirect("/")


# 3. BOT CREATION AND LOGIC SECTION -----------------------


@app.route("/create", methods=["GET"])
def show_bot_form():
    """Displays a bot creation form."""

    return render_template("create.html")


@app.route("/create", methods=["POST"])
def create_bot():
    """Adds bot to DB."""

    name = request.form.get('name')
    desc = request.form.get('description')
    data_source = request.form.get('twitter')
    icon = request.form.get('icon')

    tweets = ' '.join(get_tweets(data_source))
    source = Source(content_type='twitter',
                    content_source=data_source,
                    content=tweets)
    
    db.session.add(source)
    db.session.commit()

    bot = Bot(bot_name=name,
                creator_id = session['user_id'],
                bot_description=desc,
                bot_icon=icon,
                content_id=source.source_id,
                date_created=datetime.today())
    
    db.session.add(bot)
    db.session.commit()
    
    flash('It lives....it lives!')
    

    return redirect("/")


# 3. POST CREATION AND LOGIC SECTION -----------------------


@app.route("/post", methods=["POST"])
def create_post():
    """Generates a new post from sources."""

    bot_id = request.form.get('bot_id')
    bot = Bot.query.filter(bot_id==bot_id).first()
    text = make_text(make_chains(bot.source.content, 2), 1)

    post = Post(bot_id=bot_id,
                content=text,
                date_created=datetime.today())

    db.session.add(post)
    db.session.commit()

    return redirect("/bot/" + bot_id)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
