# Authors: Tom De Smedt, Frederik Vaassen, Vincent Van Asch
# CLiPS Computational Linguistics & Psycholinguistics Research Group
# University of Antwerp, 2010

# You need the Pattern module to run the experiment: http://www.clips.ua.ac.be/pages/pattern
# You need NodeBox for OpenGL to run the visualizer: http://cityinabottle.org/nodebox
# You need SentiWordNet for the opinion mining: http://sentiwordnet.isti.cnr.it/
# Instructions on how to install SWN in Pattern can be found in the docs (pattern.en > WordNet).

import os, sys; sys.path.append("/users/tom/desktop/pattern") # path to Pattern module.
import glob
import re
import datetime
import time
import codecs
import md5

# This script uses the pattern.web module to collect tweets 
# containing the names of Belgian politicians,
# translate them to English so they can be processed with SentiWordNet,
# and store them in daily CSV-files.
from pattern import web 
from pattern.en.wordnet import sentiment

# --------------------------------------------------------------------------------------------------
# Load SentiWordNet.
# Function sentiment_score() is called on each tweet translated to English.
sentiment.load()

def sentiment_score(s):
    v = 0
    for w in s.split(" "):
        w = w.strip(",.!?)(#:;\"\'").lower()
        if w in sentiment:
            v = v + sentiment[w][0] - sentiment[w][1]
    return v

# --------------------------------------------------------------------------------------------------
# Build the list of candidates to query for.
# Each item in the list is a (query, name, party, district)-tuples.
# For example: (u'alain mathot', u'MATHOT Alain', u'PS', u'Luik').
candidates = []
parties = []
for f in glob.glob(os.path.join("candidates", "*")):
    # The district is in the filename: kiesk_antwerpen.txt => ANTWERPEN.
    district = u"" + os.path.basename(f).replace("kiesk_", "").replace(".txt", "")
    party = None
    for line in open(f, "rU").readlines():
        if '---' in line or '===' in line:
            party = None
        if party is None: # We have a new party.
            if re.match('\d+', line):
                party = ' '.join(line.split()[3:]).decode("utf-8")
                party = party.replace(" KANDIDATEN:", "")
                parties.append(party.lower())
        else:
            candidate = re.search('(\d+)\s+-\s+(.*)', line)
            if candidate:
                candidate = candidate.group(2)
                candidate = candidate.rstrip('OPVOLGERS:').rstrip('OPLVOLGERS:').strip()
                candidate = candidate.decode('utf8')
                q = candidate.split(" ") # Switch last and first name for the search query.
                q = " ".join(q[-1:]+q[:-1])
                q = q.lower()
                candidates.append((q, candidate, party, district))

# --------------------------------------------------------------------------------------------------
# Cache search queries on a daily basis in the /cache folder.
# This way we can restart the miner if it fails, and reuse the cached results.
today = datetime.datetime.today()
today = ("%s-%s-%s") % (today.day, today.month, today.year)
web.cache.path = os.path.join("cache", today)

# --------------------------------------------------------------------------------------------------
# Create a unicode CSV file to store results.
# Put the current date in the filename for reference.
# Note: you can also use the pattern.table module to create CSV-files,
# but this module didn't exist yet at the time of the experiment.
filename = "harvest_%s.txt" % today
if not os.path.exists(filename):
    f = open(filename, "w")
    f.write(codecs.BOM_UTF8)
    f.close()

# Open today's CSV file in append-mode.
harvest = open(filename, "a")

# --------------------------------------------------------------------------------------------------
# Build an index of tweets we already did yesterday.
# Each tweet is assigned an id based on the query, tweet message and date.
# Those with an id already in the CSV files don't need to pass through Google translate.
SEEN = {}
for f in glob.glob("harvest*.txt"):
    f = open(f)
    s = f.read(); f.close()
    if s == "":
        continue
    s = s.strip().split("\n")
    s = [x.split("\t") for x in s]
    for x in s:
        if len(x) != 10:
            # This row wasn't saved correctly, probably something to do with \n or \t
            print "check %s %s" % (f, s)
        else:
            SEEN[web.u(x[0])] = True

# --------------------------------------------------------------------------------------------------
# After a few days we stopped mining for all candidates 
# and simply scanned for tweets on the top 100 most frequently mentioned.
#top100 = [
#    u'bart de wever', u'didier reynders', u'marianne thyssen', u'alexandra colen', u'alexander de croo', 
#    u'charles michel', u'yves leterme', u'jo\xeblle milquet', u'caroline gennez', u'elio di rupo', 
#    u'pieter de crem', u'olivier maingain', u'michel daerden', u'freya piryns', u'filip dewinter', 
#    u'louis michel', u'rik torfs', u'eva brems', u'johan vande lanotte', u'fran\xe7ois bellot', 
#    u'frank vandenbroucke', u'jean-marie dedecker', u'steven vanackere', u'geert bourgeois', 
#    u'anne de baetzelier', u'guy vanhengel', u'geert lambert', u'philippe moureaux', u'stefaan de clerck', 
#    u'paul magnette', u'pascal smet', u'bert anciaux', u'annemie turtelboom', u'siegfried bracke', 
#    u'bruno tobback', u'rudy demotte', u'alain destexhe', u'rudy aernoudt', u'wouter de vriendt', 
#    u'lode vereeck', u'laurette onkelinx', u'alain mathot', u'bruno valkeniers', u'carl devlies', 
#    u'sabine laruelle', u'rik daems', u'hans bonte', u'dirk van der maelen', u'tom maes', u'melchior wathelet', 
#    u'inge vervotte', u'beno\xeet lutgen', u'andr\xe9 antoine', u'louis ide', u'ingrid lieten', 
#    u'freya van den bossche', u'tine van rompuy', u'meyrem almaci', u'isabelle durant', u'gwendolyn rutten', 
#    u'vincent van quickenborne', u'philippe henry', u'christos doulkeridis', u'thierry vanhecke', 
#    u'philippe engels', u'olivier deleuze', u'marijke pinoy', u'marc wellens', u'christiane vienne', 
#    u'catherine fonck', u'bruno tuybens', u'willy demeyer', u'richard miller', u'pierre lebrun', 
#    u'peter mertens', u'paul-henry gendebien', u'patrick janssens', u'olivier baum', u'mischa\xebl modrikamen', 
#    u'marie-christine marghem', u'lorin parys', u'geert vercruyce', u'yvan mayeur', u'tinne van der straeten', 
#    u'st\xe9phanie meunier', u'sarah turine', u'raoul hedebouw', u'pol van den driessche', u'philippe close', 
#    u'kris daels', u'jef van damme', u'jan jambon', u'frieda brepoels', u'danny pieters', u'christian brotcorne', 
#    u'bram van braeckevelt', u'ben weyts', u'armand de decker', u'wouter beke', u'stijn bex'
#]
#candidates = [x for x in candidates if x[0] in top100]

# --------------------------------------------------------------------------------------------------
# Google translate for Dutch and French tweets.
translate = web.Google().translate

# --------------------------------------------------------------------------------------------------
# We'll query for tweets on each candidate.
# Twitter can handle 150+ queries per hour (actual amount is undisclosed).
# There are 2078 candidates.
# Let's do one run in ten hours.
# That means: 207.8 queries per hour, or 17.3 seconds between each query.
delay = 3600.0 / len(candidates) * 10 # 10 means 10 hours
delay = 1 # Disable the timer for testing purposes.
engine = web.Twitter(throttle=delay)

# --------------------------------------------------------------------------------------------------
# The main search algorithm.
# Traverse all candidates.
for query, name, party, district in candidates:
    # If twitter is not responding, lay off and try again in 10 minutes.
    # Otherwise, fail for this candidate.
    try: tweets = engine.search(query, start=1, count=100) # 100 tweets per politician.
    except Exception, e:
        time.sleep(600)
        try: tweets = engine.search(query, start=1, count=100)
        except:
            print "error", web.bytestring(query)
            tweets = []
    # Process each tweet on each politician.
    for i, tweet in enumerate(tweets):
        try:
            txt1 = web.plaintext(tweet.description)
            txt1 = txt1.replace("#", "# ").replace("  ", " ") # Clean twitter hashtags
            txt1 = txt1.replace("\n", " ").replace("  ", " ")
            txt1 = txt1.replace("\t", " ").replace("  ", " ")
            # Create a unique id based on candidate name, tweet and tweet date.
            # If we already have this one we don't need to Google-translate / store it again.
            id = md5.new(web.bytestring(query+"###"+txt1+"###"+tweet.date)).hexdigest()
            if id not in SEEN:
                # Google translate to English:
                language = tweet.language or "nl"
                if language == "en":
                    txt2 = txt1
                else:
                    txt2 = translate(txt1, input=language, output="en") # 100 tweets, Google is gonna love this.
                    txt2 = web.plaintext(txt2)
                score = sentiment_score(txt2)
                # Save as a tab-delimited line in today's CSV file.
                # Each line has a unique id, the query, candidate name, party, district, 
                # tweet language, original tweet, English translation, sentiment score, tweet date. For example:
                # - 0cf4baad3a5fc836db602286fe3763a5
                # - annemie turtelboom
                # - TURTELBOOM Annemie
                # - Open VLD
                # - antwerpen
                # - nl
                # - Turtelboom wil meldingsplicht voor incidenten cybercrime: Minister van Binnenlandse Zaken Annemie Turtelboom (Op... http://bit.ly/mq7MRK
                # - Turtelboom reporting incidents to cyber crime: Minister for Home Affairs Annemie Turtelboom (Rev. .. http://bit.ly/mq7MRK
                # - 0.5
                # - Sat, 11 Jun 2011 14:59:52 +0000
                s = "\t".join((id, query, name, party, district, language, txt1, txt2, str(score), tweet.date))
                harvest.write(web.bytestring(s)+"\n")
        except Exception, e:
            print "error:", web.bytestring(query), i, e
    print "done ---", query, len(tweets) # Done for this politician.

harvest.close()