import nltk
from twitter import Twitter, OAuth
from config import *
from model import Source
import markovify



# Initialize our twitter session
t = Twitter(
    auth=OAuth(access_token, token_secret, api_key, api_secret))

def open_and_read_file(file):
    """Take file path as string; return text as string.
    Takes a string that is a file path, opens the file, and returns
    the file's contents as one string of text.
    """

    with open(file) as opened_file:
        text = opened_file.read()
        text = text.replace('\n', ' ')

    return text

# def process_files(*args):
#
#     text = ""
#     for file in args:
#         text += open_and_read_file(file)
#
#     return text

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
    # request, and stops either after 30 requests or when the API doesn't
    # return any more data

    while len(tweets) > 1 and requests < 30:

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
            break

    return text_list

def process_source(content_type, content_source):

    if content_type == "text_file":

        content = open_and_read_file(content_source)

    elif content_type == "twitter":

        tweets = get_tweets(content_source)
        content = (' '.join(tweets.replace('\n', ' ')).split()

        for item in content:
            if 'http' in item or '@' in item:
                print(f"removing {item}")
                content.remove(item)

        content = ' '.join(content)

    elif content_type == "nltk":

        nltk.download(content_source)
        text = getattr(nltk.corpus, content_source)
        content =  ' '.join(text.words())

    else:

        print("Invalid source! Aborting...")

    return content
