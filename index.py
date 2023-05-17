import os
import logging
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
		selectLambda(resrc,shots,minhist)
		return doRender("first.htm")
	return doRender("calculate.htm")
if __name__ == '__main__':
	  app.run(host='127.0.0.1', port=8080, debug=True)
