from twython import Twython
import datetime
import time
import pickle

from bdw.algorithm.twitter_scrape_functions import save_tweets
from bdw.algorithm.twitter_api_keys import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

twitter = Twython(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

tweets =[]
ids = []
COUNT_OF_TWEETS_TO_BE_FETCHED = 3000
twitter_qs = ["jdceulaer"]
twitter_todo = "user" # user/search/...

# for i in range(0,MAX_ATTEMPTS):
for twitter_q in twitter_qs:
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
            results = twitter.get_user_timeline(screen_name=twitter_q,count=200)
            tweets = save_tweets(results,tweets, ids, twitter_todo)
        else:
            # After the first call we should have max_id from result of previous call. Pass it in query.
            try:
                results = twitter.get_user_timeline(screen_name=twitter_q,max_id=ids[-1],count=200)
                tweets = save_tweets(results,tweets, ids, twitter_todo)
                
                # Get out of loop if last tweet has been reached
                if ids[-1] == ids[-2]:
                    break
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
    
    # Save tweets
    if twitter_todo == "user":
        pickle.dump(tweets, open("bdw/algorithm/twitter_users/results/tweets_" + twitter_q + ".p", "wb"), protocol=2)
    elif twitter_todo == "search":
        pickle.dump(tweets, open(".../results/tweets_about_" + twitter_q + ".p", "wb"), protocol=2)