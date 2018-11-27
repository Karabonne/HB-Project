import markovify
import nltk

from flask import current_app

from config import *
from twitter import Twitter, OAuth
from model import Source


# Initialize our twitter session
t = Twitter(
    auth=OAuth(access_token, token_secret, api_key, api_secret))


def get_upload(data):
    if data['content_type'] == "text_file":
        data_source = []
        file_list = request.files.getlist("text_file")
        for file in file_list:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data_source.append("uploads/" + filename)

    content = process_source(content_type, data_source)


def open_and_read_file(file):
    """Take file path as string; return text as string.
    Takes a string that is a file path, opens the file, and returns
    the file's contents as one string of text.
    """

    with open(file) as opened_file:
        try:
            text = opened_file.read().rstrip()
            text = text.replace('\n', ' ').replace('\t', ' ')
        except UnicodeDecodeError:
            current_app.logger.warn('Could not read or replace text.')

    return text


def concatenate_files(file_list):
    return ''.join([open_and_read_file(file) for file in file_list])


def get_tweets(username):
    """
    Get tweets from a user, strip out all data except text, then
    create a list. Each item in the list is the text content of a single
    tweet by the user. Retweets are excluded from this."""

    # just a safeguard while testing, keeps API request limit low
    requests = 0

    # note: this makes 200 'requests' to the Twitter API - the actual
    # number of things returned will likely be less than that, as the
    # API still includes retweets and repilies in the count, even though
    # we discard them

    tweets = t.statuses.user_timeline(screen_name=username,
                                          trim_user="true",
                                          include_rts="false",
                                          exclude_replies="false",
                                          count=200)
    requests += 1
    text_list = [item['text'] for item in tweets]

    # this loop uses the last tweet id as the starting point for the next
    # request, and stops when the API doesn't return any more data

    while len(tweets) > 1:

        try:
            print("length = " + str(len(tweets)))
            print("last tweet id = " + str(tweets[-1]['id']))

            tweets = t.statuses.user_timeline(
                                  screen_name=username,
                                  trim_user="true",
                                  include_rts="false",
                                  exclude_replies="false",
                                  count=200,
                                  max_id=tweets[-1]['id'])

            for item in tweets:
                text_list.append(item['text'])

            requests += 1

        except TwitterHTTPError as error:
            print(error)
            return False

    return text_list


def process_source(content_type, content_source):

    if content_type == "text_file":

        content = process_files(content_source)
        # content = open_and_read_file(content_source)

    elif content_type == "twitter":

        tweets = get_tweets(content_source)
        if tweets == False:
            return False

        content = ' '.join(tweets)
        content = content.replace('\n', ' ').split()

        for item in content:
            if 'http' in item or '@' in item:
                print(f"removing {item}")
                content.remove(item)

        content = ' '.join(content)

    elif content_type == "nltk":

        nltk.download(content_source)
        text = getattr(nltk.corpus, content_source)
        # FIXME: The nltk error stays that 'text' does not have a words() method. Make sure correct object here!
        content =  ' '.join(text.words())

    else:

        print("Invalid source! Aborting...")
        return False

    return content
