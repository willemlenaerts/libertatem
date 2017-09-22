import pickle
import pattern

from pattern.web import Twitter, plaintext
from pattern.db  import Datasheet
from pattern.nl  import sentiment as sentiment_nl
# from pattern.fr  import sentiment as sentiment_fr

tweets = list()                  

tweets_text = pickle.load(open("twitter_data/input_data/zuurtegraad/tweets_Pensioenspook.p","rb"))

tweets_text_dummy = []
if type(tweets_text[0]) == dict:
    for tweet in tweets_text:
        tweets_text_dummy.append(tweet["text"])

tweets_text= tweets_text_dummy

# Sentiment analysis
avg_polarity = 0
avg_subjectivity = 0
for tweet in tweets_text:
    tweets.append(dict())
    tweets[-1]["text"] = tweet
    s = plaintext(tweet)
    tweets[-1]["sentiment"] = sentiment_nl(s)

# Remove tweets with sentiment = (0,0)
tweets_refined = []
for tweet in tweets:
    if tweet["sentiment"] != (0,0):
        tweets_refined.append(tweet)

for tweet in tweets_refined:  
    avg_polarity +=tweet["sentiment"][0]
    avg_subjectivity +=tweet["sentiment"][1]

avg_polarity = avg_polarity/len(tweets_refined)
avg_subjectivity = avg_subjectivity/len(tweets_refined)

print(avg_polarity)
print(avg_subjectivity)
