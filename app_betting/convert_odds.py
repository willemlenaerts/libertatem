# For all type of odds (Decimal/Fraction/Moneyline)

# Convert them to implied probabilities
def moneyline(odds):
    if type(odds) is str:
        odds = float(odds)
    if odds < 0:
        implied_probability = -odds/(-odds+100)
    else:
        implied_probability = 100/(odds + 100)
        
    return implied_probability
    
def decimal(odds):
    if type(odds) is str:
        odds = float(odds)
        
    implied_probability = 1/odds
    
    return implied_probability
    
def fraction(odds):
    # Assuming odds is a string "X/Y"
    implied_probability = int(odds.split("/")[1])/(int(odds.split("/")[0]) + int(odds.split("/")[1]))
    
    return implied_probability
    
# Convert moneyline to decimal
def moneyline_to_decimal(odds):
    implied_probability = moneyline(odds)
    decimal_odds = 1/implied_probability
    
    return decimal_odds
    
def probability_to_decimal(prob):
    if type(prob) is str:
        prob = float(prob)
    decimal_odds = 1/prob
    
    return decimal_odds