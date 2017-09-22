# Get INPUT data for UEFA elo/montecarlo analysis

# UEFA Champions league and Europa League games from www.uefa.com (via PyCharm Selenium)
# Elo data from clubelo.com/UCL and clubelo.com/UEL

# Return list
# [0][0]: Team Names
# [0][1]: Current Elo of Teams        

# [1]: numpy array of size (total games x 4)
#       [1][:,0]: Home Team (As a number, alphabetically as in [0]
#       [1][:,1]: Away Team (As a number, alphabetically as in [0]
#       [1][:,2]: Home Team Goals
#       [1][:,3]: Away Team Goals
#       [1][:,4]: Game already played (1 = yes, 0 = no)
   
 
def get_elo_data(date):
    # Date is a timestamp
    
    from urllib import request
    import numpy as np
    import datetime
    import pickle
    import csv
    
    output = []
    now = datetime.datetime.now()
    if date < now:
        url = "http://api.clubelo.com/" + str(date.year) + "-" + str(date.month) + "-" + str(date.day)
    else:
        url = "http://api.clubelo.com/" + str(now.year) + "-" + str(now.month) + "-" + str(now.day)
    
    response = request.urlopen(url)
        
    csv_read = response.read()
    
    # Save the string to a file
    csvstr = str(csv_read).strip("b'")
    
    lines = csvstr.split("\\n")
    f = open("app_voetbalelo/uefa_leagues/data/team_elo.csv","w")
    for line in lines:
       f.write(line.replace('"',"") + "\n")
    f.close() 
    
    # Now make list of lists (lines) to continue calculation
    with open("app_voetbalelo/uefa_leagues/data/team_elo.csv","rt") as f:
        reader = csv.reader(f)
        teams_dummy = list(reader)
    
    team_elo = list()
    for i in range(len(teams_dummy)):
        if teams_dummy[i] != []:
            team_elo.append((teams_dummy[i][1],teams_dummy[i][4]))

    return team_elo