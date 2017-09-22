import pickle
provincies_centrum = {  "West-Vlaanderen": "51.028450, 3.044109,20mi",
                        "Oost-Vlaanderen":"51.003660, 3.800314, 20mi",
                        "Antwerpen":"51.202525, 4.770883,25mi",
                        "Vlaams-Brabant":"50.864475, 4.630359,20mi",
                        "Limburg":"50.966130, 5.5021,25mi"}
               
tweets_sentiment = dict()         
for provincie_centrum in provincies_centrum:
    tweets_sentiment[provincie_centrum] = pickle.load(open("bdw/algorithm/provincies_be/results/tweets_sentiment_in_" + provincie_centrum + ".p", "rb"))
    
