# # Start with scraping sporza for all the games
# from app_playoffs.algorithms.sporza import sporza_scrape
# wedstrijden = sporza_scrape()
import pickle
from django_soccer_power_ranking.settings import BASE_DIR
import os
path = os.path.join(BASE_DIR, "app_playoffs/algorithms/data/sporza.p")
wedstrijden = pickle.load(open(path, "rb"))  # load from file sporza.p

# wedstrijden = list van lengte totaal aantal wedstrijden in Belgische competitie 2014-2015 (=299)
# voor elke wedstrijd alle mogelijke data die van sporza.be gescrapetet is

# Convert this data
from app_playoffs.algorithms.game_to_team import game_to_team
wedstrijden_gtt = game_to_team(wedstrijden)

# wedstrijden_gtt = data van wedstrijden getransformeerd tot bruikbare input voor rest van analyse
# wedstrijden_gtt[competition][0][0]:   team namen van ploegen in deze competitie
# wedstrijden_gtt[competition][0][1]:   indices van ploegen in deze competitie (gebaseerd op alfabetische lijst van alle ploegen)

# wedstrijden_gtt[competition][1]:      array van size (aantal wedstrijden in deze competitie x 5)

# Calculate ELO
from app_playoffs.algorithms.ELO_algorithm import elo
elo = elo(wedstrijden_gtt)

# elo() functie breidt wedstrijden_gtt[competition][1] array uit met win/tie/loss percentages per wedstrijd
# daarnaast genereert elo de laatste elo waarde van elke ploeg (na de laatste speeldag), en dit voor alle competities

# Add probability data to all games
from app_playoffs.algorithms.ELO_algorithm import extend_upcoming_prob
extend_upcoming_prob(wedstrijden,wedstrijden_gtt)

# extend_upcoming_prob() functie breidt wedstrijden uit met win/tie/loss percentages zoals in wedstrijden_gtt

# Forecast games and ranking using Montecarlo algorithm
from app_playoffs.algorithms.montecarlo import montecarlo
ranking_forecast = montecarlo(wedstrijden_gtt,simulations = 10000)

# montecarlo() functie genereert league_ranking_distribution voor alle competities