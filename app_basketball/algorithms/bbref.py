import time
import json
import string
import pandas
import logging
import requests

from bs4 import BeautifulSoup

BASKETBALL_LOG = 'basketball.log'

logging.basicConfig(filename=BASKETBALL_LOG,
                    level=logging.DEBUG,
                   )

__all__ = ['buildPlayerDictionary', 'searchForName', 'savePlayerDictionary', 'loadPlayerDictionary']

def getSoupFromURL(url, supressOutput=False):
    """
    This function grabs the url and returns and returns the BeautifulSoup object
    """
    if not supressOutput:
        print(url)

    while True:
        try:
            r = requests.get(url)
            return BeautifulSoup(r.text)
        except:
            time.sleep(1)
            # return None

    # return BeautifulSoup(r.text)

def getCurrentPlayerNamesAndURLS(current=False,supressOutput=False):

    names = []

    for letter in string.ascii_lowercase:
        letter_page = getSoupFromURL('http://www.basketball-reference.com/players/%s/' % (letter), supressOutput)

        # ACTIVE Players: we know that all the currently active players have <strong> tags, so we'll limit our names to those
        if current == True:
            current_names = letter_page.findAll('strong')
            for n in current_names:
                name_data = n.findChildren()[0]
                names.append((name_data.contents[0], 'http://www.basketball-reference.com' + name_data.attrs['href']))
            time.sleep(1) # sleeping to be kind for requests

        # ALL Players
        if current == False:
            try:
                current_names = letter_page.find(id="players").find("tbody").findAll("a")
            except: # No players found
                continue
            for i in range(len(current_names)):
                if "/players/" not in current_names[i].get("href"):
                    current_names[i] = None
            current_names = [var for var in current_names if var] # Remove None's
            for n in current_names:
                names.append((n.text, 'http://www.basketball-reference.com' + n.get("href")))
            time.sleep(1) # sleeping to be kind for requests


    # Fix for players with same name
    names_list = []
    urls_list = []
    for name in names:
        names_list.append(name[0])
        count = 0
        for i in range(len(names_list[:-1])):
            if name[0] == names_list[i]:
                names_list[-1] = name[0] + str(count+1)
                count += 1
        urls_list.append(name[1])

    names_dict = dict()
    for i in range(len(names_list)):
        names_dict[names_list[i]] = urls_list[i]

    return names_dict

# # Test names_dict
# for name in names_dict:
#     name["overview_url"]



def buildPlayerDictionary(supressOutput=False):
    """
    Builds a dictionary for all current players in the league-- this takes about 10 minutes to run!
    """

    logging.debug("Begin grabbing name list")
    playerNamesAndURLS = getCurrentPlayerNamesAndURLS(supressOutput)
    logging.debug("Name list grabbing complete")

    players={}
    for name, url in playerNamesAndURLS.items():
        players[name] = {'overview_url':url}
        players[name]['overview_url_content'] = None
        players[name]['gamelog_url_list'] = []
        players[name]['gamelog_data'] = None
        # players[name]['data'] = dict()

    logging.debug("Grabbing player overview URLs")

    for i, (name, player_dict) in enumerate(players.items()):
        if players[name]['overview_url_content'] is None:
            if not supressOutput:
                print(i,)

            overview_soup = getSoupFromURL(players[name]['overview_url'], supressOutput)
            players[name]['overview_url_content'] = overview_soup
            # players[name]['overview_url_content'] = ""

            # the links to each year's game logs are in <li> tags, and the text contains 'Game Logs'
            # so we can use those to pull out our urls.
            for li in overview_soup.find_all('li'):
                if 'Game Logs' in li.getText():
                    game_log_links =  li.findAll('a')

            # Get data


            for game_log_link in game_log_links:
                players[name]['gamelog_url_list'].append('http://www.basketball-reference.com' + game_log_link.get('href'))

            time.sleep(1) # sleep to be kind.

    logging.debug("buildPlayerDictionary complete")

    return players

def searchForName(playerDictionary, search_string):
    """Case insensitive partial search for player names, returns a list of strings,
    names that contained the search string.  Uses difflib for fuzzy matching.
    """
    search_string = search_string.lower()
    return [name for name in playerDictionary.keys() if search_string in name.lower()]


def savePlayerDictionary(playerDictionary, pathToFile):
    """Saves player dictionary to a JSON file"""
#    for name, k in players.items():
#        player_archive[name] = {'gamelog_url_list':k['gamelog_url_list'],
#                                'overview_url':k['overview_url'],
#                                'overview_url_content':k['overview_url_content']}

    json.dump(playerDictionary, open(pathToFile, 'w'), indent=0)

def loadPlayerDictionary(pathToFile):
    """Loads previously saved player dictionary from a JSON file"""
    f = open(pathToFile)
    json_string = f.read()
    return json.loads(json_string)

### Functions to parse the gamelogs

def dfFromGameLogURLList(gamelogs):
    """Takes a list of game log urls and returns a concatenated DataFrame"""
    return pandas.concat([dfFromGameLogURL(g) for g in gamelogs])

def dfFromGameLogURL(url):
    """Takes a url of a player's game log for a given year, returns a DataFrame"""
    glsoup = getSoupFromURL(url)

    reg_season_table = glsoup.findAll('table', attrs={'id': 'pgl_basic'})  # id for reg season table
    playoff_table = glsoup.findAll('table', attrs={'id': 'pgl_basic_playoffs'}) # id for playoff table

    # parse the table header.  we'll use this for the creation of the DataFrame

    header = []
    for th in reg_season_table[0].findAll('th'):
        if not th.getText() in header:
            header.append(th.getText())

    # add in headers for home/away and w/l columns. a must to get the DataFrame to parse correctly

    header[5] = u'HomeAway'
    header.insert(7, u'WinLoss')

    reg = soupTableToDF(reg_season_table, header)
    playoff = soupTableToDF(playoff_table, header)

    if reg is None:
        return playoff
    elif playoff is None:
        return reg
    else:
        return pandas.concat([reg, playoff])

def soupTableToDF(table_soup, header):
    """Parses the HTML/Soup table for the gamelog stats.

    Returns a pandas DataFrame
    """
    if not table_soup:
        return None
    else:
        rows = table_soup[0].findAll('tr')[1:]  # all rows but the header

        # remove blank rows
        rows = [r for r in rows if len(r.findAll('td')) > 0]

        parsed_table = [[col.getText() for col in row.findAll('td')] for row in rows] # build 2d list of table values

        for row in parsed_table:
            if len(row) == 9:
                row.extend(21*[''])

        return pandas.io.parsers.TextParser(parsed_table, names=header, index_col=2, parse_dates=True).get_chunk()

def gameLogs(playerDictionary, name):

    ### would be nice to put some caching logic here...
    return dfFromGameLogURLList(playerDictionary[name]['gamelog_url_list'])