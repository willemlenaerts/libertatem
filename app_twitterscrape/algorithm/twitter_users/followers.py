from twython import Twython
import datetime
import time
import pickle

from bdw.algorithm.twitter_scrape_functions import save_tweets
from bdw.algorithm.twitter_api_keys import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

twitter = Twython(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter_q = "jdceulaer"

# Get followers
followers = twitter.get_followers_ids(screen_name = twitter_q,cursor = -1)
follower_ids = followers["ids"]
while len(followers["ids"]) == 5000:
    followers = twitter.get_followers_ids(screen_name = twitter_q,cursor = followers["next_cursor"])
    follower_ids = follower_ids + followers["ids"]

# Save
pickle.dump(follower_ids, open("bdw/algorithm/twitter_users/results/followers_" + twitter_q + ".p", "wb"), protocol=2)

# Get number for followers for all these ids
tweeters = list()
for follower_id in follower_ids:
    try:
        tweeters.append(dict())
        a = twitter.show_user(user_id=follower_id)
        tweeters[-1]["id"] = follower_id
        tweeters[-1]["screen_name"] = a["screen_name"]
        tweeters[-1]["followers_count"] = a["followers_count"]
    except:
        print("Completion percentage = " + str(round(1000*(len(tweeters)/len(follower_ids)))/10)+ "%")
        print("Remaining limit = " + twitter.get_lastfunction_header('x-rate-limit-remaining'))
        print("Time of reset = " + datetime.datetime.fromtimestamp(int(twitter.get_lastfunction_header('x-rate-limit-reset'))).strftime("%H:%M:%S"))
        print("Wait " + str(round((int(twitter.get_lastfunction_header('x-rate-limit-reset'))-time.time())/60)) + " minutes")
        time.sleep(int(twitter.get_lastfunction_header('x-rate-limit-reset'))-time.time() + 60)