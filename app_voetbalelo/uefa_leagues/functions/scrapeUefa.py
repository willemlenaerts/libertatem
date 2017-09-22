import time
import pickle
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
import datetime

seasons = list(range(2016,2017))
for i in range(len(seasons)):
    if seasons[i] == 2007:
        seasons.pop(i)
        break

games = dict()
games["ucl"] = dict()
games["uel"] = dict()
teams = []
leagues = games.keys()


display = Display(visible=0, size=(1024, 768))
display.start()

driver = webdriver.Firefox()

team_logos = dict()

for league in leagues:
    games[league]["HomeTeam"] = list()
    games[league]["AwayTeam"] = list()
    games[league]["FTHG"] = list()
    games[league]["FTAG"] = list()
    games[league]["LOC"] = list()
    games[league]["TYPE"] = list()
    games[league]["DATE"] = list()
    games[league]["S"] = list()
    games[league]["REF"] = list()
    for season in seasons:
        start = time.time()
        if league == "ucl":
            url = "http://www.uefa.com/uefachampionsleague/season=" + str(season) + "/matches/all/index.html"
        elif league == "uel":
            url = "http://www.uefa.com/uefaeuropaleague/season=" + str(season) + "/matches/all/index.html"
        driver.get(url)
        time.sleep(30)

        soup = BeautifulSoup(driver.find_element_by_class_name("matchesall").get_attribute("innerHTML"))

        # Get data
        games_list = soup.find_all('tbody') #, class_=lambda x: x and x.startswith('tb_')

        for game in games_list:
            # S
            games[league]["S"].append(str(season-1) + "-" +  str(season)[2:])

            # DATE
            date = game.find(class_="b dateT").text
            if date[-1] == " ":
                date = date[:-1]
            games[league]["DATE"].append(datetime.datetime.strptime(date,"%d %B %Y"))

            # TYPE
            if game.find(class_="gname") == None:
                try:
                    games[league]["TYPE"].append(game.find(class_="rname").text)
                except:
                    games[league]["TYPE"].append("")
            else:
                try:
                    games[league]["TYPE"].append(game.find(class_="rname").text + game.find(class_="gname").text.replace("(","").replace(")",""))
                except:
                    games[league]["TYPE"].append("")

            # HomeTeam
            games[league]["HomeTeam"].append(game.find(class_="home").find("a").get("title"))
            if "/" in games[league]["HomeTeam"][-1]:
                games[league]["HomeTeam"][-1] = games[league]["HomeTeam"][-1].replace("/"," ")

            # AwayTeam
            games[league]["AwayTeam"].append(game.find(class_="away").find("a").get("title"))
            if "/" in games[league]["AwayTeam"][-1]:
                games[league]["AwayTeam"][-1] = games[league]["AwayTeam"][-1].replace("/"," ")

            # # Check if image is already saved
            # if games[league]["HomeTeam"][-1] not in team_logos.keys():
            #     teams.append(games[league]["HomeTeam"][-1])
            #     img_url = game.find_all(class_="logo")[0].find("img").get("src")
            #     team_logos[games[league]["HomeTeam"][-1]] = img_url
            #     img = urlopen(img_url)
            #     # localFile = open('results/logos/' + games[league]["HomeTeam"][-1]   + '.png', 'wb')
            #     localFile = open('app_voetbalelo/uefa_leagues/data/logos/' + str(len(teams)-1)   + '.png', 'wb')
            #     localFile.write(img.read())
            #     localFile.close()

            # if games[league]["AwayTeam"][-1] not in team_logos.keys():
            #     teams.append(games[league]["AwayTeam"][-1])
            #     img_url = game.find_all(class_="logo")[1].find("img").get("src")
            #     team_logos[games[league]["AwayTeam"][-1]] = img_url
            #     img = urlopen(img_url)
            #     # localFile = open('results/logos/' + games[league]["AwayTeam"][-1]   + '.png', 'wb')
            #     localFile = open('app_voetbalelo/uefa_leagues/data/logos/' + str(len(teams)-1)   + '.png', 'wb')
            #     localFile.write(img.read())
            #     localFile.close()

            # Score
            # FTHG
            if "-" not in game.find(class_="score").text:
                games[league]["FTHG"].append("")
            else:
                games[league]["FTHG"].append(game.find(class_="score").text.split("-")[0])

            # FTAG
            if "-" not in game.find(class_="score").text:
                games[league]["FTAG"].append("")
            else:
                games[league]["FTAG"].append(game.find(class_="score").text.split("-")[1])

            # LOC
            try:
                games[league]["LOC"].append(game.find(class_="referee_stadium").text.split("Stadium: ")[1].rstrip())
            except:
                games[league]["LOC"].append(game.find(class_="referee_stadium").text.split("  ")[1][:-1].lstrip().encode('ascii', 'ignore').lstrip().decode('utf8'))

            # REF
            ref = game.find(class_="referee_stadium").text.split("Stadium: ")[0]

            if ")" in ref:
                try:
                    ref = ref.split("Referee: ")[1].split(")")[0] + ")"
                except:
                    ref = ""
            else:
                ref = ""
            games[league]["REF"].append(ref)

        # Timing
        stop = time.time()
        print("Season: " + str(season) + "-" +  str(season+1)[2:] + " || Time: " + str(round(stop-start)) + " s || ET: " + str(round(stop-start)*(2015-season)) + " s")

driver.quit()
display.stop()

pickle.dump(games,open("app_voetbalelo/uefa_leagues/data/games.p", "wb"))
# pickle.dump(teams,open("app_voetbalelo/uefa_leagues/data/teams.p", "wb"))

# # Get winners
# team_results = dict()
# driver = webdriver.Firefox()
# driver.get("http://www.uefa.com/uefachampionsleague/history/champions/index.html")
# time.sleep(5)

# # winners = driver.find_elements_by_class_name("his-win-td")
# # seasons = driver.find_elements_by_class_name("his-season-td")
# # for i in range(len(winners)):
# #     try:
# #         team_results[winners[i].find_element_by_tag_name("img").get_attribute("title")].append(seasons[i].text.replace("/","-"))
# #     except:
# #         team_results[winners[i].find_element_by_tag_name("img").get_attribute("title")] = list()
# #         team_results[winners[i].find_element_by_tag_name("img").get_attribute("title")].append(seasons[i].text.replace("/","-"))
# #
# # pickle.dump(team_results,open("results/team_results.p", "wb"))
# #
# # # Get Images for all