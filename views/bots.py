# http://flask.pocoo.org/docs/1.0/blueprints/
from flask import Blueprint
from botgarden.models import Bot

bots_bp = Blueprint('bots', __name__, template_folder='bots')


@bots_bp.route('/bots/<int:bot_id>')
def show_bot_page(bot_id):
    """TODO: Shows a bot info page, including posts and creator."""

    bot = Bot.query.get(bot_id)

    return render_template("bot.html", bot=bot)
    
    
# Add other routes ....
