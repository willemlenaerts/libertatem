import pickle
import pattern
import time

from pattern.web import Twitter, plaintext
from pattern.db  import Datasheet
from pattern.nl  import sentiment as sentiment_nl
# from pattern.fr  import sentiment as sentiment_fr

         
articles = pickle.load(open("app_sentiment/bdw/input_data/1995Januari1-2015Mei24_Bart De Wever_De Morgen.p","rb"))
start = time.time()
count = 0
for article in articles:
    article["sentiment"] = sentiment_nl(articles["tekst"])
    if count == 0:
        stop = time.time()
        print("1 iteration  : " + str(round(stop-start)) + " s")
        print("ET           : " +str(round((stop-start)*len(articles)/3600)) + " h")


# # Sentiment analysis
# avg_polarity = 0
# avg_subjectivity = 0
# for tweet in tweets_text:
#     tweets.append(dict())
#     tweets[-1]["text"] = tweet
#     s = plaintext(tweet)
#     tweets[-1]["sentiment"] = sentiment_nl(s)

# # Remove tweets with sentiment = (0,0)
# tweets_refined = []
# for tweet in tweets:
#     if tweet["sentiment"] != (0,0):
#         tweets_refined.append(tweet)

# for tweet in tweets_refined:  
#     avg_polarity +=tweet["sentiment"][0]
#     avg_subjectivity +=tweet["sentiment"][1]

# avg_polarity = avg_polarity/len(tweets_refined)
# avg_subjectivity = avg_subjectivity/len(tweets_refined)

# print(avg_polarity)
# print(avg_subjectivity)
