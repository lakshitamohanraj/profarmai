from flask import Flask, request,jsonify
from agents.coordinator_agent import run, sample_conv, get_weather_and_agri_status
# from agents.market_agent import run
from agents.weather_agent import get_weather_analysis,get_weather_related_risks
from agents.market_agent import get_market_analysis,run_market_analyzer
from agents.fetch_weather_data import fetch_and_store_weather_data,get_location_from_ip

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
    methods=["GET", "POST", "OPTIONS","PUT","DELETE"],
    allow_headers=["*"]
)

WEATHER_JSON_PATH = "./agents/weather_data.json"

def initialize_weather_data():
    """Fetch latest weather and run initial analysis."""
    try:
        print("🌦️ Fetching live weather data at startup...")
        lat, lon = get_location_from_ip()# example: Chennai coordinates
        api_key = "39a396553fba4aebbba64779bb22948d"

        # Step 1: Fetch and save the live weather data
        data = fetch_and_store_weather_data(lat, lon, api_key, WEATHER_JSON_PATH)
        if not data:
            print("⚠️ Weather data not fetched, skipping analysis.")
            return

        # Step 2: Run weather + agri analysis (your existing functions)
        weather_data_str, agri_status_str = get_weather_and_agri_status("default_user")
        get_weather_analysis(weather_data_str, agri_status_str)

        print("✅ Weather data fetched, analyzed, and cached successfully.")
    except Exception as e:
        print(f"❌ Failed to initialize weather data: {e}")

# Run it in a background thread
threading.Thread(target=initialize_weather_data, daemon=True).start()

@app.route("/coordinator", methods=["POST"])
def coordinator():
    data = request.get_json()
    user_prompt = data['user_prompt']
    session_id = data.get("user_id", "default_user")  # Use unique ID for each user/session

    ans = run(user_prompt, session_id)
    if isinstance(ans, str):
        return jsonify({"response": ans})
    elif isinstance(ans, dict):
        return jsonify(ans)
    return jsonify({"response": str(ans)})

@app.route("/marketanalysis",methods = ["GET"]) # includes research 
def market():
    # ans = get_market_analysis()
    # return ans['text']
    user_id = request.args.get("user_id")
    result = run_market_analyzer(user_id)
    return result
    

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
    email = data.get("email")
    password = data.get("password")

    user_id = dbhelper.create_user(email, password)
    if user_id:
        return jsonify({"message": "User registered successfully", "userid": user_id}), 201
    else:
        return jsonify({"error": "Email already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = dbhelper.get_user(email)
    if user and user[2] == password:  # user[2] is password
        return jsonify({"message": "Login successful", "userid": user[0]}), 200  # user[0] is id
    else:
        return jsonify({"error": "Invalid email or password"}), 401
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


# ---------------------------- For 2nd Version UI-----------------------------
# FARM FINANCE RECORD APIs
@app.route("/finance_record", methods=["GET"])
def api_get_finance_record():
    user_id = request.args.get("user_id")
    if user_id:
        finance = dbhelper.get_finance_records_by_user(user_id)
    else:
        finance = None
    return jsonify(finance)

@app.route("/finance_record", methods=["DELETE"])
def api_delete_finance_record():
    record_id = request.args.get("record_id", type=int)
    result = dbhelper.delete_finance_record(record_id)
    return jsonify(result)

@app.route("/finance_record", methods=["POST"])
def api_add_finance_record():
    data = request.json
    print(data)
    result = dbhelper.add_finance_record(data)
    print(result)
    return jsonify(result)

@app.route("/finance_record", methods=["PUT"])
def api_update_finance_record():
    data = request.json
    record_id = request.args.get("record_id", type=int)
    result = dbhelper.update_finance_record(record_id,data)
    return jsonify(result)


# Crop Production Record APIs
@app.route("/crop_record", methods=["GET"])
def api_get_crop_record():
    user_id = request.args.get("user_id")
    if user_id:
        crop = dbhelper.get_crop_records_by_user(user_id)
    else:
        crop = None
    return jsonify(crop)

@app.route("/crop_record", methods=["DELETE"])
def api_delete_crop_record():
    record_id = request.args.get("record_id", type=int)
    result = dbhelper.delete_crop_record(record_id)
    return jsonify(result)

@app.route("/crop_record", methods=["POST"])
def api_add_crop_record():
    data = request.json
    print(data)
    result = dbhelper.add_crop_record(data)
    print(result)
    return jsonify(result)

@app.route("/crop_record", methods=["PUT"])
def api_update_crop_record():
    data = request.json
    record_id = request.args.get("record_id", type=int)
    result = dbhelper.update_crop_record(record_id,data)
    return jsonify(result)

# Livestock Record APIs

@app.route("/livestock_record", methods=["GET"])
def api_get_livestock_record():
    user_id = request.args.get("user_id")
    if user_id:
        livestock = dbhelper.get_livestock_records_by_user(user_id)
    else:
        livestock = None
    return jsonify(livestock)

@app.route("/livestock_record", methods=["DELETE"])
def api_delete_livestock_record():
    record_id = request.args.get("record_id", type=int)
    result = dbhelper.delete_livestock_record(record_id)
    return jsonify(result)

@app.route("/livestock_record", methods=["POST"])
def api_add_livestock_record():
    data = request.json
    print(data)
    result = dbhelper.add_livestock_record(data)
    print(result)
    return jsonify(result)

@app.route("/livestock_record", methods=["PUT"])
def api_update_livestock_record():
    data = request.json
    record_id = request.args.get("record_id", type=int)
    result = dbhelper.update_livestock_record(record_id,data)
    return jsonify(result)

# Equipment Maintenance Record APIs

@app.route("/equipment_record", methods=["GET"])
def api_get_equipment_record():
    user_id = request.args.get("user_id")
    if user_id:
        equipment = dbhelper.get_equipment_records_by_user(user_id)
    else:
        equipment = None
    return jsonify(equipment)

@app.route("/equipment_record", methods=["DELETE"])
def api_delete_equipment_record():
    record_id = request.args.get("record_id", type=int)
    result = dbhelper.delete_equipment_record(record_id)
    return jsonify(result)

@app.route("/equipment_record", methods=["POST"])
def api_add_equipment_record():
    data = request.json
    print(data)
    result = dbhelper.add_equipment_record(data)
    print(result)
    return jsonify(result)

@app.route("/equipment_record", methods=["PUT"])
def api_update_equipment_record():
    data = request.json
    record_id = request.args.get("record_id", type=int)
    result = dbhelper.update_equipment_record(record_id,data)
    return jsonify(result)

# Market Seller Link Record APIs

@app.route("/marketseller_record", methods=["GET"])
def api_get_marketseller_record():
    user_id = request.args.get("user_id")
    if user_id:
        marketseller = dbhelper.get_marketseller_records_by_user(user_id)
    else:
        marketseller = None
    return jsonify(marketseller)

@app.route("/marketseller_record", methods=["DELETE"])
def api_delete_marketseller_record():
    record_id = request.args.get("record_id", type=int)
    result = dbhelper.delete_marketseller_record(record_id)
    return jsonify(result)

@app.route("/marketseller_record", methods=["POST"])
def api_add_marketseller_record():
    data = request.json
    print(data)
    result = dbhelper.add_marketseller_record(data)
    print(result)
    return jsonify(result)

@app.route("/marketseller_record", methods=["PUT"])
def api_update_marketseller_record():
    data = request.json
    record_id = request.args.get("record_id", type=int)
    result = dbhelper.update_marketseller_record(record_id,data)
    return jsonify(result)


# Market Buyer Link Record APIs


@app.route("/marketbuyer_record", methods=["GET"])
def api_get_marketbuyer_record():
    user_id = request.args.get("user_id")
    if user_id:
        marketbuyer = dbhelper.get_marketbuyer_records_by_user(user_id)
    else:
        marketbuyer = None
    return jsonify(marketbuyer)

@app.route("/marketbuyer_record", methods=["DELETE"])
def api_delete_marketbuyer_record():
    record_id = request.args.get("record_id", type=int)
    result = dbhelper.delete_marketbuyer_record(record_id)
    return jsonify(result)

@app.route("/marketbuyer_record", methods=["POST"])
def api_add_marketbuyer_record():
    data = request.json
    print(data)
    result = dbhelper.add_marketbuyer_record(data)
    print(result)
    return jsonify(result)

@app.route("/marketbuyer_record", methods=["PUT"])
def api_update_marketbuyer_record():
    data = request.json
    record_id = request.args.get("record_id", type=int)
    result = dbhelper.update_marketbuyer_record(record_id,data)
    return jsonify(result)

# Financial Summary  APIs
@app.route("/finance_summary", methods=["GET"])
def api_get_finance_summary():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    summary = dbhelper.get_financial_summary_by_user(user_id)
    return jsonify(summary)

# Farmer Profile APIs
@app.route("/farmer_profile", methods=["GET"])
def api_get_farmer_profile():
    user_id = request.args.get("user_id")
    if user_id:
        profile = dbhelper.get_farmer_profile_by_user(user_id)
    else:
        profile = None
    return jsonify(profile)

@app.route("/farmer_profile", methods=["PUT"])
def api_update_farmer_profile():
    data = request.json
    user_id = request.args.get("user_id")
    result = dbhelper.update_farmer_profile(data,user_id)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)


