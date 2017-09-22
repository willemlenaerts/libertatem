from twython import Twython
import datetime
import time
import pickle

from bdw.algorithm.twitter_scrape_functions import get_tweets, save_tweets
from bdw.algorithm.twitter_api_keys import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

twitter = Twython(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

provincies_centrum = {  "West-Vlaanderen": "51.028450, 3.044109,20mi",
                        "Oost-Vlaanderen":"51.003660, 3.800314, 20mi",
                        "Antwerpen":"51.202525, 4.770883,25mi",
                        "Vlaams-Brabant":"50.864475, 4.630359,20mi",
                        "Limburg":"50.966130, 5.5021,25mi"}

tweets =[]
ids = []
COUNT_OF_TWEETS_TO_BE_FETCHED = 5
twitter_todo = "search"

# for i in range(0,MAX_ATTEMPTS):
for provincie_centrum in provincies_centrum:
    geocode_twitter = provincies_centrum[provincie_centrum]
    count = 0
    while(COUNT_OF_TWEETS_TO_BE_FETCHED > len(tweets)):
        # break # we got 500 tweets... !!
    
        #----------------------------------------------------------------#
        # STEP 1: Query Twitter
        # STEP 2: Save the returned tweets
        # STEP 3: Get the next max_id
        #----------------------------------------------------------------#
    
        # STEP 1: Query Twitter
        if(0 == count):
            # Query twitter for data.
            # results = twitter.search(q=twitter_q, count = 200)
            results = twitter.search(lang="nl",geocode="50.8644,4.6303,20km", count = 200)
            tweets = save_tweets(results,tweets, ids, twitter_todo)
        else:
            # After the first call we should have max_id from result of previous call. Pass it in query.
            try:
                results = twitter.search(lang = "nl",geocode = "50.8644,4.6303,20km",include_entities='true',max_id=ids[-1], count = 200)
                tweets = save_tweets(results,tweets, ids, twitter_todo)
            except:
                print("Completion percentage = " + str(round(1000*(len(tweets)/COUNT_OF_TWEETS_TO_BE_FETCHED))/10)+ "%")
                print("Remaining limit = " + twitter.get_lastfunction_header('x-rate-limit-remaining'))
                print("Time of reset = " + datetime.datetime.fromtimestamp(int(twitter.get_lastfunction_header('x-rate-limit-reset'))).strftime("%H:%M:%S"))
                print("Wait " + str(round((int(twitter.get_lastfunction_header('x-rate-limit-reset'))-time.time())/60)) + " minutes")
                try:
                    time.sleep(int(twitter.get_lastfunction_header('x-rate-limit-reset'))-time.time() + 60)
                except:
                    print("Twitter API limits reached.")
                    break
    
        count += 1
    # Remove doubles
    tweets = [dict(t) for t in set([tuple(d.items()) for d in tweets])]
    
    # Sort based on date
    tweets = sorted(tweets, key=lambda k: k['date'])
    
    # Save tweets (protocol = 2, omdat pattern gebruikt wordt voor sentiment analyse (pattern enkel beschikbaar in Python 2)
    if twitter_todo == "user":
        pickle.dump(tweets, open("bdw/algorithm/provincies_be/results/tweets_" + ".p", "wb"), protocol=2)
    elif twitter_todo == "search":
        pickle.dump(tweets, open("bdw/algorithm/provincies_be/results/tweets" + "_in_" + provincie_centrum +".p", "wb"),protocol=2)
        
# # Check of 'De Wever'
# tweets_de_wever = []
# for tweet in tweets:
#     if tweet.find('De Wever') != -1:
#         tweets_de_wever.append(tweet)



