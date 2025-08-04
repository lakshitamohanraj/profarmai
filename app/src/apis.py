from flask import Flask, request
from agents.coordinator_agent import run,sample_conv
# from agents.market_agent import run
from agents.weather_agent import get_weather_analysis,get_weather_related_risks
from agents.market_agent import get_market_analysis
from flask_cors import CORS
import json
app = Flask(__name__)
CORS(app)
@app.route("/coordinator", methods=["GET"])
def coordinator():
    data = request.get_json()
    user_prompt = data['user_prompt']
    session_id = data.get("session_id", "default_user")  # Use unique ID for each user/session

    ans = run(user_prompt, session_id)
    return ans # ans['response']


@app.route("/", methods=["GET"])
def test():
    user_prompt = request.args.get("user_prompt")
    session_id = request.args.get("session_id", "default_user")
    
    ans = sample_conv(user_prompt, session_id)
    dic = {"response":ans}
    # print(ans)
    # print(type(ans))
    return json.dumps(dic)

@app.route("/marketanalysis",methods = ["GET"]) # includes research 
def market():
    ans = get_market_analysis()
    return ans['text']

@app.route("/weatheranalysis",methods = ["GET"]) # includes research
def weather_analysis():    
    ans = get_weather_analysis()
    return ans["text"]

@app.route("/weatherrisk",methods = ["GET"]) # includes research
def weather_risk():    
    ans = get_weather_related_risks()
    return ans["text"]



@app.route("/riskagent",methods = ["POST"]) # includes risk weather + market
def risk():   
    data = request.get_json()
    user_prompt = data['user_prompt']
    session_id = data.get("session_id", "default_user")  # Use unique ID for each user/session

    ans = run(user_prompt, session_id)
    return ans['response']


if __name__ == '__main__':
    app.run(debug=True)
