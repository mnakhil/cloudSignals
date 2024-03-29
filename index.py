import os
import logging
import pandas as pd
import datetime
from time import time
import matplotlib.pyplot as plt
from flask import Flask, request, render_template,redirect
from calculate.select import runInstance
from gviz_api import DataTable
app = Flask(__name__)




# various Flask explanations available at:  https://flask.palletsprojects.com/en/1.1.x/quickstart/
global auditdf
auditdf=pd.DataFrame()
def doRender(tname, values={}):
	if not os.path.isfile( os.path.join(os.getcwd(), 'templates/'+tname) ): #No such file
		return render_template('index.htm')
	return render_template(tname, **values) 

@app.route('/',methods=['GET','POST'])
def home():
	if request.method=='POST':
		resrc=int(request.form.get('resno'))
		print(type(request.form.get('resno')))
		restype=request.form.get('resType')
		if restype=="Lambda":
			runInstance(resrc,100,50,10,"buy",restype)
		return redirect(f"/calculate/{resrc}/{restype}")
	return doRender('index.htm')

global count
count=0 
    	       
@app.route('/calculate/<resrc>/<restype>',methods=['POST','GET'])
def calculate(resrc,restype):
	if request.method=='POST':
		global conn,cursor
		resrc=int(resrc)
		shots=int(request.form.get('shots'))
		minhist=int(request.form.get('minhist'))
		pth=int(request.form.get('pth'))
		buysell=request.form.get('transaction-type')
		startT=time()
		results=runInstance(resrc,shots,minhist,pth,buysell,restype)
		endT=time()
		execT=endT-startT
		var95=[]
		var99=[]
		day=[]
		prolos=[]
		prloVal=[]
		# print(results)
		for i in range(len(results)):
			var95=var95+results[i][0]
			var99=var99+results[i][1]
			day=day+results[i][2]
			prolos=prolos+results[i][3]
			prloVal=prloVal+results[i][4]
		max_length=len(day)
		
		if(len(prolos)<max_length):
			prolos.extend(['Data not present'] * (max_length - len(prolos)))
			prloVal.extend(['Nil'] * (max_length - len(prloVal)))
		
		
		vardf=pd.DataFrame({'Day':day,'Var95':var95,'Var99':var99,'Profit/Loss':prolos,'Margin':prloVal})
		# vardf['Day'] = pd.to_datetime(vardf['Day'])

		# Convert 'Var95', 'Var99', and 'Margin' columns to float datatype
		vardf['Var95'] = vardf['Var95'].astype(float)
		vardf['Var99'] = vardf['Var99'].astype(float)
		# vardf['Margin'] = vardf['Margin'].astype(float)	
		# html_df=vardf.to_html(header=True)
		average_var95 = vardf['Var95'].mean()
		average_var99 = vardf['Var99'].mean()
		mean_df = pd.DataFrame({
			
			'var95': [average_var95],
			'var99': [average_var99]
		})

		# Concatenate the mean_df with the original df
		df_concat = pd.concat([vardf, mean_df])

		# Convert the 'date' column to datetime datatype
		df_concat['Day'] = pd.to_datetime(df_concat['Day'])
		global count
		count+=1
		global auditdf
		newdf=vardf.copy()
		newdf['Margin']=pd.to_numeric(newdf['Margin'],errors='coerce')
		avgprlos=newdf['Margin'].mean()
		audata={'SNo.':count,'No of resources':resrc,'Resource Type':restype,'Price History':minhist,'Shots':shots,'Buy/Sell':buysell,'PTH':pth,'Execution Time':execT,'Profit/Loss Avg':avgprlos}
		auditdf=auditdf.append(audata,ignore_index=True)
		dates = df_concat['Day'].to_list()
		# return doRender("first.htm",{'dataframe':vardf})
		return doRender("first.htm",{'dates':day,'var95':var95,'var99':var99,'average95':average_var95,'average99':average_var99,'dataframe':vardf})
		
	
	return doRender("calculate.htm")
@app.route('/reset',methods=['GET','POST'])
def reset():
	global auditdf,count
	print(auditdf)
	shots=auditdf.at[count-1,'Shots']
	minhist=auditdf.at[count-1,'Price History']
	signal=auditdf.at[count-1,'Buy/Sell']
	pth=auditdf.at[count-1,'PTH']
	resrc=auditdf.at[count-1,'No of resources']
	restype=auditdf.at[count-1,'Resource Type']
	return doRender('calculate.htm',{'shots':shots,'minhist':minhist,'signal':signal,'pth':pth,'resrc':resrc,'restype':restype})
@app.route('/audit',methods=['GET'])
def audit():
	return doRender('audit.html',{'dataframe':auditdf})
@app.errorhandler(500)
# A small bit of error handling
def server_error(e):
    logging.exception('ERROR!')
    return """
    An  error occurred: <pre>{}</pre>
    """.format(e), 500
if __name__ == '__main__':
	  app.run(host='127.0.0.1', port=8080, debug=True)
