def get_elo_data():
    import numpy as np
    import pandas as pd
    import datetime
    import pickle
    import json
    
    output = dict()
    output["country"] = []
    output["elo"] = []
    
    # Import data from OWN EloRating of World Football
    # See sway-blog.be
    
    input_data = json.load(open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/country_table.json","r"))
    
    for country in input_data:
        output["country"].append(country["country"])
        output["elo"].append(country["nuelo"])
        
    output = pd.DataFrame(output)
    
    return output