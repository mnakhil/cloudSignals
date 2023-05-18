import os
import logging
import pandas as pd
from flask import Flask, request, render_template
from calculate.select import selectLambda
import gviz_api

app = Flask(__name__)

# various Flask explanations available at:  https://flask.palletsprojects.com/en/1.1.x/quickstart/

def doRender(tname, values={}):
	if not os.path.isfile( os.path.join(os.getcwd(), 'templates/'+tname) ): #No such file
		return render_template('index.htm')
	return render_template(tname, **values) 

@app.route('/')
def home():
  return doRender("index.htm")
	    	       
@app.route('/calculate',methods=['POST','GET'])
def calculate():
	if request.method=='POST':
		resrc=int(request.form.get('resrc'))
		shots=int(request.form.get('shots'))
		minhist=int(request.form.get('minhist'))
		pth=int(request.form.get('pth'))
		results=selectLambda(resrc,shots,minhist,pth)
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
		vardf['Day'] = pd.to_datetime(vardf['Day'])

		# Convert 'Var95', 'Var99', and 'Margin' columns to float datatype
		vardf['Var95'] = vardf['Var95'].astype(float)
		vardf['Var99'] = vardf['Var99'].astype(float)
		vardf['Margin'] = vardf['Margin'].astype(float)	
		# html_df=vardf.to_html(header=True)
		average_var95 = vardf['Var95'].mean()
		average_var99 = vardf['Var99'].mean()
		average_marg = vardf['Margin'].mean()
		
		return doRender("first.htm",{'dataframe':vardf})
		# return render_template("first.htm",dataframe=vardf)
	return doRender("calculate.htm")
if __name__ == '__main__':
	  app.run(host='127.0.0.1', port=8080, debug=True)
