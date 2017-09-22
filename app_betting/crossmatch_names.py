# Input: 2 lists of teams
# Output: dict with teams_odds as keys and teams_elo as values

def crossmatch_names(teams_odds,teams_elo):
    import distance
    from fuzzywuzzy import fuzz
    
    output = dict()
    for team_odds in teams_odds:
        distance_dummy = []
        for team_elo in teams_elo:
            if fuzz.ratio(team_odds.lower(),team_elo.lower()) == 100:
                distance_dummy = [(100,team_elo)]
                break
            distance_dummy.append((fuzz.partial_ratio(team_odds.lower(),team_elo.lower()),team_elo))
        
        # Check highest distance (== closest string match)
        # output.append([team_odds,sorted(distance_dummy, reverse=True)[0][1]])
        output[team_odds] = sorted(distance_dummy, reverse=True)[0][1]
    
    return output