import pickle
provincies_centrum = {  "West-Vlaanderen": "51.028450, 3.044109,20mi",
                        "Oost-Vlaanderen":"51.003660, 3.800314, 20mi",
                        "Antwerpen":"51.202525, 4.770883,25mi",
                        "Vlaams-Brabant":"50.864475, 4.630359,20mi",
                        "Limburg":"50.966130, 5.5021,25mi"}
                        
for provincie_centrum in provincies_centrum:
    tweets = pickle.load(open("bdw/algorithm/provincies_be/results/tweets_in_" + provincie_centrum + ".p","rb"))
    # pickle.dump(tweets, open("bdw/algorithm/provincies_be/results/tweets_in_" + provincie_centrum + ".p", "wb"),protocol=2)
    # # Check sentiment
    from bdw.algorithm.aia_SentimentAnalysis import test_sentiment
    # Reconvert datetime into string for sentiment analysis
    for tweet in tweets:
        tweet["date"] = tweet["date"].strftime('%a %b %d %H:%M:%S +0000 %Y')
    
    tweets_sentiment = test_sentiment.test_sentiment(tweets)
    pickle.dump(tweets_sentiment, open("bdw/algorithm/provincies_be/results/tweets_sentiment_in_" + provincie_centrum + ".p", "wb"))