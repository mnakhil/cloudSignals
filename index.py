import os
import logging
import pandas as pd
from flask import Flask, request, render_template
from calculate.select import selectLambda
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
		results=selectLambda(resrc,shots,minhist)
		var95=[]
		var99=[]
		day=[]
		print(results)
		for i in range(len(results)):
			var95=var95+results[i][0]
			var99=var99+results[i][1]
			day=day+results[i][2]
		
		print(len(day))
		print(len(var95))
		print(len(var99))
		vardf=pd.DataFrame({'Day':day,'Var95':var95,'Var99':var99})	
		html_df=vardf.to_html(header=True)
		return doRender("first.htm",{'table':html_df})
	return doRender("calculate.htm")
if __name__ == '__main__':
	  app.run(host='127.0.0.1', port=8080, debug=True)
