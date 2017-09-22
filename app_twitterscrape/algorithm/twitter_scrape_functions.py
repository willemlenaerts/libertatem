def save_tweets(results, tweets, ids, twitter_todo):
    import datetime
    # STEP 2: Save the returned tweets
    if twitter_todo == "user":
        for result in results:
                tweet_text = result['text']
                tweet_date = datetime.datetime.strptime(result["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
                if type(result['user']) == dict:
                    tweet_user = result['user']["screen_name"]
                else:
                    tweet_user = result['user']
                tweets.append({"user":tweet_user,"text":tweet_text,"date":tweet_date})

                ids.append(result["id"])
    elif twitter_todo == "search":
        for result in results["statuses"]:
                tweet_text = result['text']
                tweet_date = datetime.datetime.strptime(result["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
                if type(result['user']) == dict:
                    tweet_user = result['user']["screen_name"]
                else:
                    tweet_user = result['user']
                tweets.append({"user":tweet_user,"text":tweet_text,"date":tweet_date})
                ids.append(result["id"])
    return tweets