def get_elo_team(team,team_elo):
    import distance
    output_elo = 0
    
    # Fixed assign
    team_names_panda_fixed = ["AZ","Astana","Asteras","Rubin","Sion","Celtic","Shakhtar Donetsk","Mönchengladbach","Paris","Krasnodar","Club Brugge","Lokomotiv Moskva","Qarabağ","St-Étienne","Sporting CP","Qäbälä","Plzeň","Liberec","Gent","Athletic"]
    team_names_elo_fixed = ["Alkmaar","FK Astana","Asteras Tripolis","Rubin Kazan","Sion","Celtic","Shakhtar","Gladbach","Paris SG","FC Krasnodar","Brugge","Lok Moskva","Karabakh Agdam","Saint-Etienne","Sporting","Gabala","Viktoria Plzen","Slovan Liberec","Gent","Bilbao"]
    for k in range(len(team_names_panda_fixed)):
        if team == team_names_panda_fixed[k]:
            for j in range(len(team_elo)):
                if team_elo[j][0] == team_names_elo_fixed[k]:
                    output_elo = team_elo[j][1]
    
    # Rest
    if output_elo == 0:
        for j in range(len(team_elo)):
            if distance.levenshtein(team,team_elo[j][0]) == 0:
                output_elo = team_elo[j][1]
                break
            elif distance.levenshtein(team,team_elo[j][0]) == 1:
                output_elo = team_elo[j][1]
                break
            elif distance.levenshtein(team,team_elo[j][0]) == 2:
                output_elo = team_elo[j][1]
                break

    return float(output_elo)