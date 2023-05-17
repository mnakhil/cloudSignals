import math
import random
import time
import boto3
import yfinance as yf
import pandas as pd
import requests
import json
import http.client
from datetime import date, timedelta
from pandas_datareader import data as pdr
from concurrent.futures import ThreadPoolExecutor
# override yfinance with pandas – seems to be a common step
def selectLambda(resrc,shots,minhist):
	yf.pdr_override()

	# Get stock data from Yahoo Finance – here, asking for about 3 years
	today = date.today()
	decadeAgo = today - timedelta(days=1095)

	# Get stock data from Yahoo Finance – here, Gamestop which had an interesting
	#time in 2021: https://en.wikipedia.org/wiki/GameStop_short_squeeze

	data = pdr.get_data_yahoo('GME', start=decadeAgo, end=today)
	data.reset_index(inplace=True)
	data.rename(columns={'Date': 'Date'}, inplace=True)
	data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
	# data.reset_index(inplace=True)
	
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
	
	# data['date']=data.index
	runs=[value for value in range(resrc)]
	resultsList=[]
	datap=data.to_dict(orient='records')

	var95=[]
	var99=[]
	list95=[]
	list99=[]
	day=[]
	def getpage(id):
		try:
			payload = {
					'data': datap,
					'shots': shots,
					'minhist': minhist,
			}
			json_payload = json.dumps(payload)
			# print(json_payload)
			# Invoke the Lambda function
			# lambda_client = boto3.client('https://ghxbycdfza.execute-api.us-east-1.amazonaws.com/default')

			# response = lambda_client.invoke(
			# 	FunctionName='testFunction',
			# 	InvocationType='RequestResponse',
			# 	Payload=json_payload
			# )
			response=requests.post("https://ghxbycdfza.execute-api.us-east-1.amazonaws.com/default/testFunction",json=json_payload)
			data=response.json()
			print(data)
			
			var95=json.loads(data['var95'])
			var99=json.loads(data['var99'])
			date=json.loads(data['date'])
			# print(var95)
			print(var95)
			return [var95,var99,date]
		except IOError:
			print( 'Failed to open ', host ) # Is the Lambda address correct?
		
	
	def getpages():
		lvar95=[]
		lvar99=[]
		tempdate=[]
		with ThreadPoolExecutor() as executor:
			result=executor.map(getpage, runs)
			results=list(result)
			for i in range(len(results)):
				lvar95=lvar95+results[i][0]
				lvar99=lvar99+results[i][1]
				tempdate=tempdate+results[i][2]
			# print(lvar95)
		return [lvar95,lvar99,tempdate]
		# return list(result)
	

	result=getpages()
	resultsList.append(result)
	# print(result)
	# print(resultsList)
	
	return resultsList		
			

	    	       
