from models import *


def bot_sources_factory(bot_data):
    """Returns a bot with source.
    Ex.
    bot_data = {'content_type': 'data',
                'content_source': 'source',
                'content': 'content',
                'bot_name': 'name',
                'creator_id': 'id',
                'bot_desc': 'desc',
                'bot_icon': 'icon'}
                
    :params bot_data: a dictionary containing source and bot data
    :returns: an instance of Bot
    """
    
    source = Source(content_type=bot_data['content_type'],
                    content_source=bot_data['data_source'],
                    content=bot_data['content'])

    db.session.add(source)
    db.session.commit()

    bot = Bot(bot_name=bot_data['bot_name'],
              creator_id = bot_data['creator_id'],
              bot_description=bot_data['bot_desc'],
              bot_icon=bot_data['bot_icon'],
              source_id=source.source_id)

    db.session.add(bot)
    db.session.commit()
    
    return bot


def source_factory(source_data):
    """"Create and return a source instance."""
    source = Source(content_type=source_data['content_type'],
                    content_source=source_data['data_source'],
                    content=source_data['content'])

    db.session.add(source)
    db.session.commit()
    
    return source


def bot_factory(bot_data):
    """Create and return a bot instance."""
    bot = Bot(bot_name=bot_data['bot_name'],
              creator_id = bot_data['creator_id'],
              bot_description=bot_data['bot_desc'],
              bot_icon=bot_data['bot_icon'],
              source_id=bot_data['source_id'])

    db.session.add(bot)
    db.session.commit()
    
    return bot
