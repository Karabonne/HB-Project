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
        try:
            text = opened_file.read().rstrip()
            text = text.replace('\n', ' ')
            #text = text.replace('\0', ' ')
            text = text.replace('\t', ' ')
        except UnicodeDecodeError:
            return " "

    return text

def process_files(file_list):

    text = ""
    for file in file_list:
        text += open_and_read_file(file)

    return text

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
    """Add sources to the database. Sources are built as follows:

    1. read from input file, contains the following:
        content_type|content_source
    2. for twitter sources:
            grab username from 'content_source', retrieve all tweets, collate
            the text into one large string
        for nltk sources:
            retrieve corpus name from 'content_source', download from
            nltk database if required, and use nltk functions to store corpus
            as one large text file
    3. add above to database
    """
    
    if content_type == "text_file":

        content = process_files(content_source)
        # content = open_and_read_file(content_source)

    elif content_type == "twitter":

        tweets = get_tweets(content_source)
        if tweets == False:
            return False

        term_list = ' '.join(tweets)
        term_list = term_list.replace('\n', ' ').split()

        content = []

        for item in term_list:
            if 'http' in item or 'https' in item:
                print(item)
            elif item[0] == '#' or item[0] == '@':
                print(item)
            else:
                content.append(item)

        content = ' '.join(content)

    elif content_type == "nltk":

        nltk.download(content_source)
        text = getattr(nltk.corpus, content_source)
        content =  ' '.join(text.words())

    else:

        print("Invalid source! Aborting...")
        return False

    return content
