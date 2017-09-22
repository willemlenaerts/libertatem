from app_sentiment.sa_aia.aia_api.aia_SentimentAnalysis import aia_SentimentAnalysisAPI
from bdw.algorithm.aia_SentimentAnalysis.aia_api_key import API
# Input: tweets, a list of strings (tweets)
# Output:

def test_sentiment(tweets):

    # Instantiation of the class. Please note that the "api" object behaves
    # like a ordinary Python list, and you can do with it everything you can do with a ordinary Python list
    api = aia_SentimentAnalysisAPI.aia_SentimentAnalysisAPI(API,sentiment_classifier="default")

    for tweet in tweets:
        api.append({"text": tweet["text"], "language_iso": "nld"})
    # api.append({"text": "The hotel maid is very nice.", "language_iso": "eng"})
    # api.append({"text": "Additionally, the breakfast was horrible.", "language_iso": "eng"})
    # api.append({"text": "Loved the swimming pool.", "language_iso": "eng"})
    # api.append({"text": "I was here last summer, and I won't be here ever again", "language_iso": "eng"})
    # api.append({"text": "I must say that the personnel was unfriendly", "language_iso": "eng"})

    # This is the processing call. You can specify whether you wish to receive the verbose output updates on what the API call is doing at any time.
    # The results of the processing will be automatically appended to the objects in the "api" list, whilst the process() call returns the summary of
    # the processing as returned by the API itself.
    summary = api.process(verbose=True)

    return api