import pickle
import pattern

from pattern.web import Twitter, plaintext
from pattern.db  import Datasheet
from pattern.nl  import sentiment as sentiment_nl
# from pattern.fr  import sentiment as sentiment_fr

provincies_centrum = {  "West-Vlaanderen": "51.028450, 3.044109,20mi",
                        "Oost-Vlaanderen":"51.003660, 3.800314, 20mi",
                        "Antwerpen":"51.202525, 4.770883,25mi",
                        "Vlaams-Brabant":"50.864475, 4.630359,20mi",
                        "Limburg":"50.966130, 5.5021,25mi"}
sentiment = dict()                  
for provincie_centrum in provincies_centrum:
    tweets = pickle.load(open("twitter_data/input_data/provincies_be/tweets_in_" + provincie_centrum + ".p","rb"))
    sentiment[provincie_centrum] = list()
    # Sentiment analysis
    for tweet in tweets:
        s = plaintext(tweet["text"])
        tweet["sentiment"] = sentiment_nl(s)
    