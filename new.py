import math
import random
import time
import yfinance as yf
import pandas as pd
import requests
import http.client
from datetime import date, timedelta
from pandas_datareader import data as pdr
from concurrent.futures import ThreadPoolExecutor
# override yfinance with pandas – seems to be a common step
yf.pdr_override()

# Get stock data from Yahoo Finance – here, asking for about 3 years
today = date.today()
decadeAgo = today - timedelta(days=1095)

# Get stock data from Yahoo Finance – here, Gamestop which had an interesting
#time in 2021: https://en.wikipedia.org/wiki/GameStop_short_squeeze

data = pdr.get_data_yahoo('GME', start=decadeAgo, end=today)
data = pd.DataFrame.from_dict(data)
# Other symbols: TSLA – Tesla, AMZN – Amazon, ZM – Zoom, ETH-USD – Ethereum-Dollar etc.

# Add two columns to this to allow for Buy and Sell signals
# fill with zero
data['Buy']=0
data['Sell']=0


# Find the signals – uncomment print statements if you want to
# look at the data these pick out in some another way
# e.g. check that the date given is the end of the pattern claimed

for i in range(2, len(data)):

    body = 0.01

       # Three Soldiers
    if (data.Close[i] - data.Open[i]) >= body  \
and data.Close[i] > data.Close[i-1]  \
and (data.Close[i-1] - data.Open[i-1]) >= body  \
and data.Close[i-1] > data.Close[i-2]  \
and (data.Close[i-2] - data.Open[i-2]) >= body:
        data.at[data.index[i], 'Buy'] = 1
        #print("Buy at ", data.index[i])

       # Three Crows
    if (data.Open[i] - data.Close[i]) >= body  \
and data.Close[i] < data.Close[i-1] \
and (data.Open[i-1] - data.Close[i-1]) >= body  \
and data.Close[i-1] < data.Close[i-2]  \
and (data.Open[i-2] - data.Close[i-2]) >= body:
        data.at[data.index[i], 'Sell'] = 1
        #print("Sell at ", data.index[i])

# Data now contains signals, so we can pick signals with a minimum amount
# of historic data, and use shots for the amount of simulated values
# to be generated based on the mean and standard deviation of the recent history
parallel = 10
runs=[value for value in range(parallel)]
minhistory = 100
shots = 100
resultsList=[]
for i in range(minhistory, len(data)):
	if data.Buy[i]==1: # if we’re interested in Buy signals
		mean=data.Close[i-minhistory:i].pct_change(1).mean()
		std=data.Close[i-minhistory:i].pct_change(1).std()
		def getpage(id):
		    try:
		    	json={'key1': mean,'key2': std,'key3': shots}
		    	#json= '{ "key1": "'+str(mean)+'","key2":"'+str(std)+'","key3":"'+str(shots)+'"}'
		    	response=requests.post("https://ghxbycdfza.execute-api.us-east-1.amazonaws.com/default/testFunction",json=json)
		    	data=response.json()
		    	print(data)
		    	return data
		    except IOError:
		    	print( 'Failed to open ', host ) # Is the Lambda address correct?
		  

		def getpages():
		    with ThreadPoolExecutor() as executor:
		    	results=executor.map(getpage, runs)
		    return list(results)
		result=getpages()
		
		#print(result)

	    	       
