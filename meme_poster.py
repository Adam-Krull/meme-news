#Imports
import datetime
import numpy as np
import os
import json
import time
import tweepy

from env import X_API_KEY, X_SECRET_KEY, X_CLIENT, X_CLIENT_SECRET

#Establish today's date
today = datetime.date.today().strftime('%Y-%m-%d')

#Establish path to approved memes
filepath = os.path.join(today, 'approved.json')

#Load in approved memes
with open(filepath, 'r') as f:
    approved = json.load(f)

#Authenticate with the v1.1 API
def one_auth(con_key=X_API_KEY, con_secret=X_SECRET_KEY, access_key=X_CLIENT, access_secret=X_CLIENT_SECRET):

    """Takes in the various API keys for the X developer account.
    
    Returns the tweepy v1.1 API class object that will be used to upload media."""

    auth = tweepy.OAuth1UserHandler(con_key, con_secret,
                                    access_key, access_secret)
    
    api = tweepy.API(auth)

    print('X API v1.1 authentication achieved.')

    return api

#Authenticate with the v2.0 API
def two_auth(con_key=X_API_KEY, con_secret=X_SECRET_KEY, access_key=X_CLIENT, access_secret=X_CLIENT_SECRET):

    """Takes in the various API keys for the X developer account.
    
    Returns the tweepy v2.0 Client class object for creating tweets."""

    client = tweepy.Client(consumer_key=con_key, consumer_secret=con_secret,
                            access_token=access_key, access_token_secret=access_secret)
    
    print('X API v2.0 authentication achieved.')

    return client

#Upload a meme to the X media API endpoint
def upload_meme(auth_api, filepath):

    """Takes in the authenticated API object from tweepy.
    
    Uploads the meme image to the X media API endpoint.
    
    Returns the media id string in a one-item list."""

    response = auth_api.media_upload(filepath)

    media_string = [response.media_id_string]

    print('Meme uploaded! Media string returned.')

    return media_string

#Add hashtags to the headline to complete my tweet text content
def curate_content(headline):

    """Takes in the news headline as a string.
    
    Returns a string with additional hashtags."""

    hashtags = ' #currentevents #memenews'

    return headline + hashtags

#Post the content to X
def create_tweet(auth_client, media_string, headline):

    """Takes the authenticated client, the media string, and the headline.
    
    Posts a tweet to X with the content."""

    response = auth_client.create_tweet(media_ids=media_string, text=headline)

    print('Tweet created!')

#Sleep for a random amount of time
def sleepy(rng):

    """Takes in a random number generating object.
    
    Sleeps for a random number of seconds between 10-20."""

    seconds = rng.integers(low=10, high=20, size=1)[0]

    print(f'Sleeping for {seconds} seconds.')

    time.sleep(seconds)

#Pipeline function to post my memes to X
def post_tweets(today=today, memes=approved):

    """Takes in today's date.
    
    Posts all approved memes to X."""

    #Get API v1.1 authentication
    media_auth = one_auth()

    #Get API v2.0 authentication
    client_auth = two_auth()

    #Create random number object
    rng = np.random.default_rng()

    #Loop through approved memes
    for meme in memes:

        #Extract the two pieces of information
        filepath = meme['image']
        headline = meme['headline']

        #Upload the meme to the media API endpoint
        media_string = upload_meme(media_auth, filepath)

        #Customize the tweet text
        tweet_body = curate_content(headline)

        #Create the tweet
        create_tweet(client_auth, media_string, tweet_body)

        #Pause between tweets
        sleepy(rng)

    print(f'Meme posting complete! Posted {len(memes)} new memes to X today.')

#Execute the pipeline function
if __name__ == '__main__':

    post_tweets()        