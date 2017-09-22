# This file will populate database
import os
import numpy as np

def populate():
    competitions = ["rs","poi","poii_a","poii_b","poiii"]
    speeldagen_rs = 30
    speeldagen_poi = 10
    speeldagen_poii_a = 6
    speeldagen_poii_b = 6
    speeldagen_poiii = 5
    
    # Remove previous data in table
    import django
    django.setup()
    
    game_data.objects.all().delete()
    
    speeldagen.objects.all().delete()
    
    standings_rs.objects.all().delete()
    standings_poi.objects.all().delete()
    standings_poii_a.objects.all().delete()
    standings_poii_b.objects.all().delete()
    standings_poiii.objects.all().delete()
    
    elo_data_rs.objects.all().delete()
    elo_data_poi.objects.all().delete()
    elo_data_poii_a.objects.all().delete()
    elo_data_poii_b.objects.all().delete()
    elo_data_poiii.objects.all().delete()
    
    # Start with scraping sporza for all the games
    # from app_voetbalelo.jpl_playoffs.algorithms.sporza import sporza_scrape
    # wedstrijden = sporza_scrape()
    import pickle
    from exergos.settings import BASE_DIR
    import os
    path = os.path.join(BASE_DIR, "app_voetbalelo/jpl_playoffs/algorithms/data/sporza.p")
    wedstrijden = pickle.load(open(path, "rb"))  # load from file sporza.p
    
    # Convert this data
    from app_voetbalelo.jpl_playoffs.algorithms.game_to_team import game_to_team
    wedstrijden_gtt = game_to_team(wedstrijden)
    
    for competition in competitions:
        team_names = wedstrijden_gtt[competition][0][0]
        team_indices = wedstrijden_gtt[competition][0][1]
        number_of_teams = len(team_names)
        # Fill database
        for i in range(number_of_teams): # For every team
            d_standings = {'rank' : wedstrijden_gtt[competition][2][i,8],
                            'team' : wedstrijden_gtt[competition][0][0][i], 
                            'games' : wedstrijden_gtt[competition][2][i,0], 
                            'win' : wedstrijden_gtt[competition][2][i,1], 
                            'loss' : wedstrijden_gtt[competition][2][i,2], 
                            'tie' : wedstrijden_gtt[competition][2][i,3], 
                            'goals_for' : wedstrijden_gtt[competition][2][i,4], 
                            'goals_against' : wedstrijden_gtt[competition][2][i,5], 
                            'goal_difference' : wedstrijden_gtt[competition][2][i,6], 
                            'points' : wedstrijden_gtt[competition][2][i,7]}
            
            if competition == "rs":
                standings_rs.objects.create(**d_standings)
            if competition == "poi":
                standings_poi.objects.create(**d_standings)
            if competition == "poii_a":
                standings_poii_a.objects.create(**d_standings)
            if competition == "poii_b":
                standings_poii_b.objects.create(**d_standings)
            if competition == "poiii":
                standings_poiii.objects.create(**d_standings)
            
    # Calculate ELO
    from app_voetbalelo.jpl_playoffs.algorithms.ELO_algorithm import elo
    elo = elo(wedstrijden_gtt)
    
    # Add probability data to all games
    from app_voetbalelo.jpl_playoffs.algorithms.ELO_algorithm import extend_upcoming_prob
    extend_upcoming_prob(wedstrijden,wedstrijden_gtt)
    
    # Forecast games and ranking using Montecarlo algorithm
    from app_voetbalelo.jpl_playoffs.algorithms.montecarlo import montecarlo
    ranking_forecast = montecarlo(wedstrijden_gtt,simulations = 10000)
    
    for competition in competitions:
        team_names = ranking_forecast[competition][0][0]
        team_indices = ranking_forecast[competition][0][1]
        number_of_teams = len(team_names)
        speeldagen_rs = 30
        
        for i in range(len(team_names)): # For every team    
            # d is dictionary of field names and values
            d_elo = {'team' : team_names[i],'elo' : int(elo[competition][1][i])}
            for j in range(number_of_teams):
                d_elo['finish_%s' % (j+1)] = ranking_forecast[competition][1][i,j]
                
            if competition == "rs":
                elo_data_rs.objects.create(**d_elo)
            if competition == "poi":
                elo_data_poi.objects.create(**d_elo)    
            if competition == "poii_a":
                elo_data_poii_a.objects.create(**d_elo)
            if competition == "poii_b":
                elo_data_poii_b.objects.create(**d_elo)
            if competition == "poiii":
                elo_data_poiii.objects.create(**d_elo)
    
        # Speeldagen
        d_speeldagen = dict()
        team_names_all = ranking_forecast["rs"][0][0]
        for i in range(len(team_names_all)):
            # rs
            team_names = ranking_forecast["rs"][0][0]
            team_indices = ranking_forecast["rs"][0][1]
            number_of_teams = len(team_names)
            d_speeldagen['team'] = team_names[i]
            for speeldag in range(speeldagen_rs): 
                d_speeldagen['elo_rs_speeldag_%s' % int((speeldag+1))] = elo["rs"][2][team_indices[i]][speeldag]
                d_speeldagen['ranking_rs_speeldag_%s' % int((speeldag+1))] = wedstrijden_gtt["rs"][3][team_indices[i]][speeldag]
                d_speeldagen['points_rs_speeldag_%s' % int((speeldag+1))] = wedstrijden_gtt["rs"][4][team_indices[i]][speeldag]
            
            # poi
            team_names = ranking_forecast["poi"][0][0]
            team_indices = ranking_forecast["poi"][0][1]
            number_of_teams = len(team_names)
            # enkel volledige speeldag uploaden
            gespeeld = 0
            for j in range(len(elo["poi"][2])):
                gespeeld = gespeeld + len(elo["poi"][2][j])
            gespeeld = int(np.floor(gespeeld/number_of_teams))
                
            for j in range(len(team_names)):
                if team_names[j] == team_names_all[i]:
                    for speeldag in range(gespeeld):
                        d_speeldagen['elo_poi_speeldag_%s' % int((speeldag+1))] = elo["poi"][2][j][speeldag]
                        d_speeldagen['ranking_poi_speeldag_%s' % int((speeldag+1))] = wedstrijden_gtt["poi"][3][j][speeldag]
                        d_speeldagen['points_poi_speeldag_%s' % int((speeldag+1))] = wedstrijden_gtt["poi"][4][j][speeldag]   
            
            # poii_a
            team_names = ranking_forecast["poii_a"][0][0]
            team_indices = ranking_forecast["poii_a"][0][1]
            number_of_teams = len(team_names)
            gespeeld = 0
            for j in range(len(elo["poii_a"][2])):
                gespeeld = gespeeld + len(elo["poii_a"][2][j])
            gespeeld = int(np.floor(gespeeld/number_of_teams))
            for j in range(len(team_names)):
                if team_names[j] == team_names_all[i]:
                    for speeldag in range(gespeeld): 
                        d_speeldagen['elo_poii_a_speeldag_%s' % int((speeldag+1))] = elo["poii_a"][2][j][speeldag]
                        d_speeldagen['ranking_poii_a_speeldag_%s' % int((speeldag+1))] = wedstrijden_gtt["poii_a"][3][j][speeldag]
                        d_speeldagen['points_poii_a_speeldag_%s' % int((speeldag+1))] = wedstrijden_gtt["poii_a"][4][j][speeldag]
            
            # poii_b
            team_names = ranking_forecast["poii_b"][0][0]
            team_indices = ranking_forecast["poii_b"][0][1]
            number_of_teams = len(team_names)
            gespeeld = 0
            for j in range(len(elo["poii_b"][2])):
                gespeeld = gespeeld + len(elo["poii_b"][2][j])
            gespeeld = int(np.floor(gespeeld/number_of_teams))
            for j in range(len(team_names)):
                if team_names[j] == team_names_all[i]:
                    for speeldag in range(gespeeld): 
                        d_speeldagen['elo_poii_b_speeldag_%s' % int((speeldag+1))] = elo["poii_b"][2][j][speeldag]
                        d_speeldagen['ranking_poii_b_speeldag_%s' % int((speeldag+1))] = wedstrijden_gtt["poii_b"][3][j][speeldag]
                        d_speeldagen['points_poii_b_speeldag_%s' % int((speeldag+1))] = wedstrijden_gtt["poii_b"][4][j][speeldag]            
            
            # poiii
            team_names = ranking_forecast["poiii"][0][0]
            team_indices = ranking_forecast["poiii"][0][1]
            number_of_teams = len(team_names)
            gespeeld = 0
            for j in range(len(elo["poiii"][2])):
                gespeeld = gespeeld + len(elo["poiii"][2][j])
            gespeeld = int(np.floor(gespeeld/number_of_teams))
            for j in range(len(team_names)):
                if team_names[j] == team_names_all[i]:
                    for speeldag in range(gespeeld): 
                        d_speeldagen['elo_poiii_speeldag_%s' % int((speeldag+1))] = elo["poiii"][2][j][speeldag]
                        d_speeldagen['ranking_poiii_speeldag_%s' % int((speeldag+1))] = wedstrijden_gtt["poiii"][3][j][speeldag]
                        d_speeldagen['points_poiii_speeldag_%s' % int((speeldag+1))] = wedstrijden_gtt["poiii"][4][j][speeldag]
        
            speeldagen.objects.create(**d_speeldagen)    
    
    # Game data        
    for game in range(len(wedstrijden)): # game result
        # d is dictionary of field names and values
        d_game_data = wedstrijden[game]
        game_data.objects.create(**d_game_data)
             
# Start execution here!
if __name__ == '__main__':
    print("Starting Soccer Power Ranking database population script...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exergos.settings')
    from app_voetbalelo.models.jpl_playoffs import game_data
    
    from app_voetbalelo.models.jpl_playoffs import speeldagen
    
    from app_voetbalelo.models.jpl_playoffs import standings_rs
    from app_voetbalelo.models.jpl_playoffs import standings_poi
    from app_voetbalelo.models.jpl_playoffs import standings_poii_a
    from app_voetbalelo.models.jpl_playoffs import standings_poii_b
    from app_voetbalelo.models.jpl_playoffs import standings_poiii
    
    from app_voetbalelo.models.jpl_playoffs import elo_data_rs
    from app_voetbalelo.models.jpl_playoffs import elo_data_poi
    from app_voetbalelo.models.jpl_playoffs import elo_data_poii_a
    from app_voetbalelo.models.jpl_playoffs import elo_data_poii_b
    from app_voetbalelo.models.jpl_playoffs import elo_data_poiii
    


    populate()