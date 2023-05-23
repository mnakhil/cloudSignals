import json
import random
from flask import Flask, jsonify, request

app=Flask(__name__)

@app.route('/cloudapi',methods=['POST'])
def post_data():
    data=request.get_data()
    return ec2c