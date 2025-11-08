from flask import Flask, request,jsonify
from agents.coordinator_agent import run, sample_conv, get_weather_and_agri_status
# from agents.market_agent import run
from agents.weather_agent import get_weather_analysis,get_weather_related_risks
from agents.market_agent import get_market_analysis
from flask_cors import CORS
import json
from models import dbhelper

import threading
import time

app = Flask(__name__)
dbhelper.init_db()
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

def initialize_weather_data():
    """Precompute weather analysis at app startup."""
    try:
        print("🌦️ Initializing weather analysis data at startup...")
        weather_data_str, agri_status_str = get_weather_and_agri_status("default_user")
        get_weather_analysis(weather_data_str, agri_status_str)
        print("✅ Weather data initialized and cached successfully.")
    except Exception as e:
        print(f"❌ Failed to initialize weather data: {e}")

# Run it in background so Flask doesn’t block startup
threading.Thread(target=initialize_weather_data, daemon=True).start()

@app.route("/coordinator", methods=["POST"])
def coordinator():
    data = request.get_json()
    user_prompt = data['user_prompt']
    session_id = data.get("session_id", "default_user")  # Use unique ID for each user/session

    ans = run(user_prompt, session_id)
    if isinstance(ans, str):
        return jsonify({"response": ans})
    elif isinstance(ans, dict):
        return jsonify(ans)
    else:
        return jsonify({"response": str(ans)})
    #return ans # ans['response']


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
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user_id = dbhelper.create_user(username, password)
    if user_id:
        return jsonify({"message": "User registered successfully", "userid": user_id}), 201
    else:
        return jsonify({"error": "Username already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = dbhelper.get_user(username)
    if user and user[2] == password:  # user[2] is password
        return jsonify({"message": "Login successful", "userid": user[0]}), 200  # user[0] is id
    else:
        return jsonify({"error": "Invalid username or password"}), 401
# Get all farms
@app.route("/farms", methods=["GET"])
def api_get_farms():
    user_id = request.args.get("user_id")  # get ?user_id=... from query params
    if user_id:
        farms = dbhelper.get_farms_by_user(user_id)
    else:
        farms = dbhelper.get_all_farms()
    return jsonify(farms)
# Add a new farm
@app.route("/farms", methods=["POST"])
def api_add_farm():
    farm_data = request.json
    result = dbhelper.add_farm(farm_data)
    return jsonify(result)

# EQUIPMENT APIs
@app.route("/equipment", methods=["GET"])
def api_get_equipment():
    user_id = request.args.get("user_id")
    if user_id:
        equipment = dbhelper.get_equipment_by_user(user_id)
    else:
        equipment = dbhelper.get_all_equipment()
    return jsonify(equipment)

@app.route("/equipment", methods=["POST"])
def api_add_equipment():
    equipment_data = request.json
    result = dbhelper.add_equipment(equipment_data)
    return jsonify(result)

# CROP APIs
@app.route("/crops", methods=["GET"])
def api_get_crops():
    user_id = request.args.get("user_id")
    if user_id:
        crops = dbhelper.get_crops_by_user(user_id)
    else:
        crops = dbhelper.get_all_crops()
    return jsonify(crops)

@app.route("/crops", methods=["POST"])
def api_add_crop():
    crop_data = request.json
    result = dbhelper.add_crop(crop_data)
    return jsonify(result)

# LIVESTOCK APIs
@app.route("/livestock", methods=["GET"])
def api_get_livestock():
    user_id = request.args.get("user_id")
    if user_id:
        livestock = dbhelper.get_livestock_by_user(user_id)
    else:
        livestock = dbhelper.get_all_livestock()
    return jsonify(livestock)

@app.route("/livestock", methods=["POST"])
def api_add_livestock():
    livestock_data = request.json
    result = dbhelper.add_livestock(livestock_data)
    return jsonify(result)
# ----------------------------
# SELLER MARKET LINK APIs
# ----------------------------
@app.route("/seller_market_link", methods=["GET"])
def api_get_seller_market_link():
    user_id = request.args.get("user_id")
    if user_id:
        seller_links = dbhelper.get_seller_market_link_by_user(user_id)
    else:
        seller_links = dbhelper.get_all_seller_market_links()
    return jsonify(seller_links)

@app.route("/seller_market_link", methods=["POST"])
def api_add_seller_market_link():
    seller_data = request.json
    result = dbhelper.add_seller_market_link(seller_data)
    return jsonify(result)


# ----------------------------
# FARM BUDGET APIs
# ----------------------------
@app.route("/farm_budget", methods=["GET"])
def api_get_farm_budget():
    user_id = request.args.get("user_id")
    if user_id:
        budgets = dbhelper.get_farm_budget_by_user(user_id)
    else:
        budgets = dbhelper.get_all_farm_budgets()
    return jsonify(budgets)

@app.route("/farm_budget", methods=["POST"])
def api_add_farm_budget():
    budget_data = request.json
    result = dbhelper.add_farm_budget(budget_data)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
