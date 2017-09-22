# Scrape data from Yahoo Finance using yahoo_finance package

from yahoo_finance import Share
yahoo = Share('YHOO')
print(yahoo.get_open())
print(yahoo.get_price())
print(yahoo.get_trade_datetime())