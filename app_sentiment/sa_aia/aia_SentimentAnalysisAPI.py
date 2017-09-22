import urllib
import json
from urllib.request import urlopen
import urllib.parse

class aia_SentimentAnalysisAPI(list):
    def __init__(self, api_key, sentiment_classifier="default",data=[]):
        self.api_key = api_key
        self.sentiment_classifier = sentiment_classifier
        list.__init__(self, data)

    def process(self,verbose=True):
        if verbose==True:
            print("Preparing data batch for processing, please wait...")
        batch = {}
        for idx in range(0,len(self)):
            if type(self[idx])==str: # type(self[idx])==unicode
                batch[idx] = {"id": idx, "text": self[idx]}
            elif type(self[idx])==dict:
                if "text" in self[idx]:
                    self[idx]["id"] = idx
                    batch[idx] = self[idx]
                else:
                    print("WARNING: Element with index "+str(idx)+" is a incorrectly formatted Dictionary object missing a 'text' field and will not be processed!")
            else:
                print("WARNING: Element with index "+str(idx)+" is not a String or Unicode object and will not be processed!")

        if verbose==True:
            print("Data batch prepared. Sending data to API and processing, please wait...")

        batch_values = []
        for i in range(len(batch)):
            batch_values.append(batch[i])

        reply = urlopen('http://api.ai-applied.nl/api/text_analysis_api/',
                            data=urllib.parse.urlencode(
                                {"request":
                                 json.dumps(
                                     {"id": 0, "data":
                                      {"api_key": self.api_key, "call":
                                       {"return_original": False,
                                        "classifier": self.sentiment_classifier,
                                        "data": batch_values
                                        }
                                       }
                                      }
                                     )
                                 }
                                ).encode("utf-8")
                            ,timeout=3600)

        reply = json.loads(reply.read().decode('utf-8'))
        if verbose==True:
            print("Data processed.")
        if reply["status"]!=1:
            raise Exception("ERROR: Something went wrong with Ai Applied's API Transport Layer. Error code: "+str(reply["status"])+". Please contact Ai Applied.")
        else:
            reply = reply["response"]
            if reply["success"]==False:
                raise Exception(reply["description"]+" Please verify that you are using correct settings, otherwise contact Ai Applied.")
            else:
                for item in reply["data"]:
                    if "id" in item:
                        if item["id"] in batch:
                            batch[item["id"]].update(item)
                        else:
                            print("WARNING: Element with index "+str(item["id"])+" is unknown locally! Please report this error to Ai Applied.")
                    else:
                        print("WARNING: Wrongly formatted reply! Please report this error to Ai Applied.")
                for item in batch:
                    self[item] = batch[item]
                    del self[item]["id"]

                del batch
                del reply["data"]

                reply = reply["description"]

                return reply

