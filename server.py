# If you modularize the app with the views folder and botgarden/__init__.py
# http://flask.pocoo.org/docs/1.0/blueprints/
from botgarden.views import bot_bp

# Current implementation ...
from views import app
from models import connect_to_db

# Same reasoning as for line 1 above ...
# http://flask.pocoo.org/docs/1.0/blueprints/
app.register_blueprint(bot_bp)


if __name__ == "__main__":
    
    # set debug mode for testing
    #app.debug = True
    # make sure templates, etc. are not cached in debug mode
    #app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    #DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
