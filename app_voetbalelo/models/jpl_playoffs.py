from django.db import models

# Define speeldagen en number_of_teams for different competitions
competitions = ["rs","poi","poii_a","poii_b","poiii"]

speeldagen_rs = 30
speeldagen_poi = 10
speeldagen_poii_a = 6
speeldagen_poii_b = 6
speeldagen_poiii = 5

class standings_rs(models.Model):
    # Field 1: Team Name
    rank = models.IntegerField(default=0)
    team = models.TextField(default='')
    # Other fields: SPI, off rating, def rating
    games = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    tie = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    
    # To loop through field names and field values in template
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in standings_rs._meta.fields]
        
class standings_poi(models.Model):
    # Field 1: Team Name
    rank = models.IntegerField(default=0)
    team = models.TextField(default='')
    # Other fields: SPI, off rating, def rating
    games = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    tie = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    # To loop through field names and field values in template
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in standings_poi._meta.fields]
        
class standings_poii_a(models.Model):
    # Field 1: Team Name
    rank = models.IntegerField(default=0)
    team = models.TextField(default='')
    # Other fields: SPI, off rating, def rating
    games = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    tie = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    # To loop through field names and field values in template
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in standings_poii_a._meta.fields]


class standings_poii_b(models.Model):
    # Field 1: Team Name
    rank = models.IntegerField(default=0)
    team = models.TextField(default='')
    # Other fields: SPI, off rating, def rating
    games = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    tie = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    
    # To loop through field names and field values in template
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in standings_poii_b._meta.fields]

class standings_poiii(models.Model):
    # Field 1: Team Name
    rank = models.IntegerField(default=0)
    team = models.TextField(default='')
    # Other fields: SPI, off rating, def rating
    games = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    tie = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    # To loop through field names and field values in template
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in standings_poiii._meta.fields]

class elo_data_rs(models.Model):
    # Field 1: Team Name
    team = models.TextField(default='')
    # Other fields: SPI, off rating, def rating
    # Save elo as integer (easier for ranking page)
    elo = models.IntegerField(default=0)

    # To loop through field names and field values in template
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in elo_data_rs._meta.fields]

# Other fields: possible league finishes (1 to 16)
for i in range(16):
    elo_data_rs.add_to_class('finish_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    
class elo_data_poi(models.Model):
    # Field 1: Team Name
    team = models.TextField(default='')
    # Other fields: SPI, off rating, def rating
    # Save elo as integer (easier for ranking page)
    elo = models.IntegerField(default=0)

    # To loop through field names and field values in template
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in elo_data_poi._meta.fields]
        
# Other fields: possible league finishes (1 to 16)
for i in range(6):
    elo_data_poi.add_to_class('finish_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    
class elo_data_poii_a(models.Model):
    # Field 1: Team Name
    team = models.TextField(default='')
    # Other fields: SPI, off rating, def rating
    # Save elo as integer (easier for ranking page)
    elo = models.IntegerField(default=0)
    
    # To loop through field names and field values in template
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in elo_data_poii_a._meta.fields]

# Other fields: possible league finishes (1 to 16)
for i in range(4):
    elo_data_poii_a.add_to_class('finish_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    
class elo_data_poii_b(models.Model):
    # Field 1: Team Name
    team = models.TextField(default='')
    # Other fields: SPI, off rating, def rating
    # Save elo as integer (easier for ranking page)
    elo = models.IntegerField(default=0)

    # To loop through field names and field values in template
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in elo_data_poii_b._meta.fields]

# Other fields: possible league finishes (1 to 16)
for i in range(4):
    elo_data_poii_b.add_to_class('finish_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    
class elo_data_poiii(models.Model):
    # Field 1: Team Name
    team = models.TextField(default='')
    # Other fields: SPI, off rating, def rating
    # Save elo as integer (easier for ranking page)
    elo = models.IntegerField(default=0)

    # To loop through field names and field values in template
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in elo_data_poiii._meta.fields]

# Other fields: possible league finishes (1 to 16)
for i in range(2):
    elo_data_poiii.add_to_class('finish_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    
# # Other fields: possible league finishes (1 to 16)
# for i in range(5):
#     elo_data.add_to_class('elo_min%s' % i, models.IntegerField(default=0))
class speeldagen(models.Model):
    team = models.TextField(default='')
    
    # To loop through field names and field values in template
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in speeldagen._meta.fields]

for i in range(speeldagen_rs):
    speeldagen.add_to_class('elo_rs_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    speeldagen.add_to_class('ranking_rs_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    speeldagen.add_to_class('points_rs_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
for i in range(speeldagen_poi):
    speeldagen.add_to_class('elo_poi_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    speeldagen.add_to_class('ranking_poi_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    speeldagen.add_to_class('points_poi_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
for i in range(speeldagen_poii_a):
    speeldagen.add_to_class('elo_poii_a_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    speeldagen.add_to_class('ranking_poii_a_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    speeldagen.add_to_class('points_poii_a_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
for i in range(speeldagen_poii_b):
    speeldagen.add_to_class('elo_poii_b_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    speeldagen.add_to_class('ranking_poii_b_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    speeldagen.add_to_class('points_poii_b_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
for i in range(speeldagen_poiii):
    speeldagen.add_to_class('elo_poiii_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    speeldagen.add_to_class('ranking_poiii_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    speeldagen.add_to_class('points_poiii_speeldag_%s' % (i+1), models.DecimalField(max_digits= 30, decimal_places= 15,default=0))
    
class game_data(models.Model):
    import datetime
    # To loop through field names and field values in template
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in game_data._meta.fields]

    # If sporza_big(number_of_seasons) is called:
    # output[season][game] =    dict()
    #                           output[season][game]["game_date"]
    #                           output[season][game]["game_hour"]
    #                           output[season][game]["host"]
    #                           output[season][game]["visitor"]
    #                           output[season][game]["played"]
    #                           output[season][game]["host_goal"]
    #                           output[season][game]["visitor_goal"]
    #                           output[season][game]["result"]
    #                           output[season][game]["referee"]
    #                           output[season][game]["stadium"]
    #                           output[season][game]["spectators"]
    #                           output[season][game]["host_goal_data"]
    #                           output[season][game]["visitor_goal_data"]
    #                           output[season][game]["host_yellow_card_data"]
    #                           output[season][game]["visitor_yellow_card_data"]
    #                           output[season][game]["host_red_card_data"]
    #                           output[season][game]["visitor_red_card_data"]
    #                           output[season][game]["host_starting_team"]
    #                           output[season][game]["visitor_starting_team"]
    #                           output[season][game]["host_substitution"]
    #                           output[season][game]["visitor_substitution"]
    #                           output[season][game]["host_manager"]
    #                           output[season][game]["visitor_manager"]
    #                           output[season][game]["minute_x"] with x from 1 tot 90
    # game_date = models.DateField() # ["%d/%m/%Y"], default=datetime.now().strftime("%d/%m/%Y")
    competition = models.TextField(default='')
    speeldag = models.TextField(default='')
    game_date = models.DateField()
    host = models.TextField(default='')
    visitor = models.TextField(default='')
    played = models.TextField(default='')
    host_goal = models.TextField(default='')
    visitor_goal = models.TextField(default='')
    result = models.TextField(default='')
    referee = models.TextField(default='')
    stadium = models.TextField(default='')
    spectators = models.TextField(default='')
    host_goal_data = models.TextField(default='')
    visitor_goal_data = models.TextField(default='')
    host_yellow_card_data = models.TextField(default='')
    visitor_yellow_card_data = models.TextField(default='')
    host_red_card_data = models.TextField(default='')
    visitor_red_card_data = models.TextField(default='')
    host_starting_team = models.TextField(default='')
    visitor_starting_team = models.TextField(default='')
    host_substitution = models.TextField(default='')
    visitor_substitution = models.TextField(default='')
    host_manager = models.TextField(default='')
    visitor_manager = models.TextField(default='')
    host_win = models.DecimalField(max_digits= 30, decimal_places= 15,default=0)
    tie = models.DecimalField(max_digits= 30, decimal_places= 15,default=0)
    visitor_win = models.DecimalField(max_digits= 30, decimal_places= 15,default=0)
    # host_spi = models.DecimalField(max_digits= 30, decimal_places= 15,default=0)
    # tie_spi = models.DecimalField(max_digits= 30, decimal_places= 15,default=0)
    # visitor_spi = models.DecimalField(max_digits= 30, decimal_places= 15,default=0)
    # upset = models.DecimalField(max_digits= 30, decimal_places= 15,default=0)
    # excitement = models.DecimalField(max_digits= 30, decimal_places= 15,default=0)


