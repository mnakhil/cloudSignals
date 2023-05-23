import json
import random
from flask import Flask, jsonify, request

app=Flask(__name__)

@app.route('/cloudapi',methods=['POST'])
def post_data():
	data=request.get_data()
	return ec2cloud(json.loads(data))
    
def ec2cloud(data):
   
    
    # json_payload = event['body']  # Assuming the JSON payload is passed in the 'body' field

    # # Deserialize JSON to dictionary
    payload = json.loads(event)

    # Access DataFrame, other variables, and host address
    
    data = payload['data']
    shots = int(payload['shots'])
    minhistory = int(payload['minhist'])
    signal = payload['signal']
    var95List=[]
    var99List=[]
    dat=[]
    
    for i in range(minhistory, len(data)):
        
        if data[i]['Buy'] == 1 and signal=="buy":  # If we're interested in Buy signals
            close_prices = [entry['Close'] for entry in data[i - minhistory:i]]
            # mean = sum(close_prices) / minhistory
            # std = (sum((x - mean) ** 2 for x in close_prices) / minhistory) ** 0.5
            
            returns = [((x - close_prices[idx - 1]) / close_prices[idx - 1]) for idx, x in enumerate(close_prices) if idx > 0]
            mean = sum(returns) / (len(returns) or 1)
            std = (sum((x - mean) ** 2 for x in returns) / (len(returns) or 1)) ** 0.5

            dat.append(data[i]['Date'])
            # Generate a much larger random number series with the same characteristics
            simulated = [random.gauss(mean, std) for _ in range(shots)]
    
            # Sort and pick 95% and 99% values
            simulated.sort(reverse=True)
            var95 = simulated[int(len(simulated) * 0.95)]
            var99 = simulated[int(len(simulated) * 0.99)]
            var95List.append(var95)
            var99List.append(var99)
            
            date=json.dumps(dat)
            var_95=json.dumps(var95List)
            var_99=json.dumps(var99List)
        
        if data[i]['Sell'] == 1 and signal=="sell":  # If we're interested in Buy signals
            close_prices = [entry['Close'] for entry in data[i - minhistory:i]]
            # mean = sum(close_prices) / minhistory
            # std = (sum((x - mean) ** 2 for x in close_prices) / minhistory) ** 0.5
            
            returns = [((x - close_prices[idx - 1]) / close_prices[idx - 1]) for idx, x in enumerate(close_prices) if idx > 0]
            mean = sum(returns) / (len(returns) or 1)
            std = (sum((x - mean) ** 2 for x in returns) / (len(returns) or 1)) ** 0.5

            dat.append(data[i]['Date'])
            # Generate a much larger random number series with the same characteristics
            simulated = [random.gauss(mean, std) for _ in range(shots)]
    
            # Sort and pick 95% and 99% values
            simulated.sort(reverse=True)
            var95 = simulated[int(len(simulated) * 0.95)]
            var99 = simulated[int(len(simulated) * 0.99)]
            var95List.append(var95)
            var99List.append(var99)
            
            date=json.dumps(dat)
            var_95=json.dumps(var95List)
            var_99=json.dumps(var99List)
        
    return {
        'var95':var_95,
        'var99':var_99,
        'date':date
    }
    
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
