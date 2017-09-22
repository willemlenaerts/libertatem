# This file will populate database

import os
import numpy as np

def populate():
    # Remove previous data in table
    import django
    django.setup()

    # # # # # # Load sporza data
    # from app_regular_season.algorithms.sporza import sporza
    # input_data = sporza("new",number_of_seasons=1)

    # Or get it from file:
    # Import previous file
    import pickle
    input_data = pickle.load(open("app_regular_season/algorithms/data/sporza_regular_season.p", "rb"))  # load from file sporza.p

    # Standings
    # Remove previous data
    standings.objects.all().delete()

    # Generate new data
    import app_regular_season.algorithms.game_to_team as gtt
    standings_data = gtt.game_to_team(input_data)

    # Fill database
    for i in range(len(standings_data[2])): # For every team
        d_standings = {'rank' :standings_data[2][i,8], 'team' : standings_data[0][i], 'games' : standings_data[2][i,0], 'win' : standings_data[2][i,1], 'loss' : standings_data[2][i,2], 'tie' : standings_data[2][i,3], 'goals_for' : standings_data[2][i,4], 'goals_against' : standings_data[2][i,5], 'goal_difference' : standings_data[2][i,6], 'points' : standings_data[2][i,7]}

        standings.objects.create(**d_standings)

    # SPI
    # Remove previous data
    spi_data.objects.all().delete()

    # Generate SPI data
    import app_regular_season.algorithms.SPI_algorithm as spi
    output_spi = spi.spi(input_data,simulations=1000)

    # output_spi is a list of 2 things
    # [0]:  List of 2 things
    # [0][0]: Team names of all teams in Jupiler Pro League
    # [0][1]: Array of size (number of teams x 3)
    #         [0][1][:,0]: SPI
    #         [0][1][:,1]: Off Rating
    #         [0][1][:,2]: Def Rating

    # [1]:  A size (number_of_teams x number_of_teams) matrix with the percentage chance of every team to end up in every
    #       possible league position

    for i in range(len(output_spi[0][0][0])): # For every team
        # this returns a dict with the property
        # name as key and the property val as its value

        # d is dictionary of field names and values
        d_spi = {'team' : output_spi[0][0][0][i],'spi' : output_spi[0][0][1][i,0], 'off_rating' : output_spi[0][0][1][i,1], 'def_rating' : output_spi[0][0][1][i,2]}
        for j in range(16):
            d_spi['finish_%s' % (j+1)] = output_spi[0][1][i,j]

        spi_data.objects.create(**d_spi)

    # ELO
    # Remove previous data
    elo_data.objects.all().delete()
    elo_data_po.objects.all().delete()

    # Generate ELO data
    import app_regular_season.algorithms.ELO_algorithm as elo
    output_elo = elo.elo(input_data,simulations=1000)
    #
    # # output_elo is a list of 2 things
    # # [0]:  List of 2 things
    # # [0][0]: Team names of all teams in Jupiler Pro League
    # # [0][1]: Array of size (number of teams x 3)
    # #         [0][1][:,0]: ELO
    #
    # # [1]:  A size (number_of_teams x number_of_teams) matrix with the percentage chance of every team to end up in every
    # #       possible league position

    for i in range(len(output_elo[0][0][0])): # For every team
        # this returns a dict with the property
        # name as key and the property val as its value

        # d is dictionary of field names and values
        d_elo = {'team' : output_elo[0][0][0][i],'elo' : int(output_elo[0][0][1][i])}
        d_elo_po = {'team' : output_elo[0][0][0][i]}
        for j in range(16):
            d_elo['finish_%s' % (j+1)] = output_elo[0][1][i,j]
            d_elo_po['finish_%s' % (j+1)] = output_elo[0][2][i,j]

        for j in range(5):
            d_elo['elo_min%s' % j] = output_elo[2][i][-1-j]

        elo_data.objects.create(**d_elo)
        elo_data_po.objects.create(**d_elo_po)
    # Game Data
    # Remove previous data
    game_data.objects.all().delete()

    # Extend input_data with SPI and ELO
    from app_regular_season.algorithms.ELO_algorithm import extend_upcoming_prob
    input_data = extend_upcoming_prob(input_data, output_elo[1], "elo")
    input_data = extend_upcoming_prob(input_data, output_spi[1], "spi")

    from app_regular_season.algorithms.ELO_algorithm import upset
    input_data = upset(input_data)

    from app_regular_season.algorithms.ELO_algorithm import excitement
    input_data = excitement(input_data)

    # Fill table with all this data
    for season in range(len(input_data)): #delta (goal difference)
        for game in range(len(input_data[season])): # game result
            # d is dictionary of field names and values
            d_game_data = input_data[season][game]
            game_data.objects.create(**d_game_data)

# Start execution here!
if __name__ == '__main__':
    print("Starting Soccer Power Ranking database population script...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_soccer_power_ranking.settings')
    from app_regular_season.models import spi_data
    from app_regular_season.models import elo_data
    from app_regular_season.models import elo_data_po
    from app_regular_season.models import standings
    from app_regular_season.models import game_data

    populate()