import sqlite3
from pathlib import Path

# Path to DB (relative to this file)
DB_PATH = Path(__file__).resolve().parent.parent / "mydatabase.db"

def get_connection():
    conn= sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row 
    return conn

# Ensure users table exists once
def init_db():
    conn = get_connection()
    cursor = conn.cursor()


    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
        # BUYER MARKET LINK
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buyer_market_link (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            market_name TEXT,
            buyer_type TEXT,
            product_categories TEXT,
            reliability_score REAL,
            preferred_payment_terms TEXT,
            farmer_selection_reason TEXT,
            financial_dependability TEXT,
            latitude TEXT,
            longitude TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # FARM
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farm (
            farm_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            farm_name TEXT,
            latitude TEXT,
            longitude TEXT,
            street TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            country TEXT,
            farm_size_acres TEXT,
            notes TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # EQUIPMENT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            equipment_type TEXT,
            make TEXT,
            model TEXT,
            status TEXT)
        
    ''')

    # CROP PRODUCTION
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crop_production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            crop_name TEXT,
            variety TEXT,
            season TEXT,
            planting_date TEXT,
            harvest_date TEXT,
            field_number TEXT,
            area_acres TEXT,
            yield_per_acre_bushels TEXT,
            soil_type TEXT,
            irrigation_method TEXT,
            fertilizer_applications TEXT,
            pest_disease_status TEXT,
            current_status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # LIVESTOCK PRODUCTION
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livestock_production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            animal_type TEXT,
            breed TEXT,
            count TEXT,
            health_status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # SELLER MARKET LINK
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seller_market_link (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            market_name TEXT,
            seller_type TEXT,
            product_categories TEXT,
            available_equipment TEXT,
            payment_terms TEXT,
            equipment_status TEXT,
            farmer_preference_reason TEXT,
            latitude TEXT,
            longitude TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # FARM BUDGET
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farm_budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            available_budget_in_inr TEXT,
            credit_limit_in_inr TEXT,
            current_debt_in_inr TEXT,
            risk_appetite TEXT,
            past_trade_performance TEXT,
            equipment_ownership TEXT,
            logistics_capability TEXT,
            investment_flexibility TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # TRANSACTIONS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            user_id TEXT,
            type TEXT,
            category TEXT,
            amount REAL,
            currency TEXT,
            date DATETIME,
            status TEXT,
            payment_method TEXT,
            reference_no TEXT,
            related_asset TEXT,
            related_liability TEXT,
            party TEXT,
            notes TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # FINANCIAL SUMMARY
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            farm_name TEXT,
            farmer_name TEXT,
            location TEXT,
            reporting_period TEXT,
            summary_date DATE,
            balance_sheet TEXT,
            income_statement TEXT,
            cash_flow_statement TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

def create_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        user_id = cursor.lastrowid  # return inserted user ID
        return user_id
    except sqlite3.IntegrityError:
        return False  # username already exists
    finally:
        conn.close()

def get_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_farms():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farm")
    farms = cursor.fetchall()
    conn.close()
    return [dict(farm) for farm in farms]
def get_farms_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farm WHERE user_id = ?", (user_id,))
    farms = cursor.fetchall()
    conn.close()
    return [dict(farm) for farm in farms]
def add_farm(farm):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO farm ( farm_name,user_id ,latitude, longitude, street, city, state, zip_code, country, farm_size_acres, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
         farm["farm_name"],farm["user_id"],  farm["latitude"], farm["longitude"],
        farm["street"], farm["city"], farm["state"], farm["zip_code"], farm["country"],
        farm["farm_size_acres"], farm["notes"]
    ))
    conn.commit()
    conn.close()
    return {"message": "Farm added successfully"}

# def update_farm(farm_id, updates):
#     conn = get_connection()
#     cursor = conn.cursor()

#     fields = []
#     values = []
#     for key, value in updates.items():
#         fields.append(f"{key} = ?")
#         values.append(value)
#     values.append(farm_id)

#     sql = f"UPDATE farm SET {', '.join(fields)} WHERE farm_id = ?"
#     cursor.execute(sql, values)
#     conn.commit()
#     conn.close()
#     return {"message": "Farm updated successfully"}

def get_all_equipment():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment")
    equipment = cursor.fetchall()
    conn.close()
    return [dict(e) for e in equipment]

def add_equipment(equipment):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO equipment (user_id, equipment_type, make, model, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        equipment["user_id"], equipment["equipment_type"], equipment["make"],
        equipment["model"], equipment["status"]
    ))
    conn.commit()
    conn.close()
    return {"message": "Equipment added successfully"}

def get_equipment_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment WHERE user_id = ?", (user_id,))
    equipment = cursor.fetchall()
    conn.close()
    return [dict(e) for e in equipment]





# CROP PRODUCTION
def get_all_crops():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crop_production")
    crops = cursor.fetchall()
    conn.close()
    return [dict(c) for c in crops]

def add_crop(crop):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO crop_production (
            user_id, crop_name, variety, season, planting_date, harvest_date,
            field_number, area_acres, yield_per_acre_bushels, soil_type,
            irrigation_method, fertilizer_applications, pest_disease_status, current_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        crop["user_id"], crop["crop_name"], crop["variety"], crop["season"],
        crop.get("planting_date"), crop.get("harvest_date"), crop.get("field_number"),
        crop.get("area_acres"), crop.get("yield_per_acre_bushels"), crop.get("soil_type"),
        crop.get("irrigation_method"), crop.get("fertilizer_applications"),
        crop.get("pest_disease_status"), crop["current_status"]
    ))
    conn.commit()
    conn.close()
    return {"message": "Crop added successfully"}
def get_crops_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crop_production WHERE user_id = ?", (user_id,))
    crops = cursor.fetchall()
    conn.close()
    return [dict(c) for c in crops]

def get_all_livestock():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livestock_production")
    livestock = cursor.fetchall()
    conn.close()
    return [dict(l) for l in livestock]

def add_livestock(livestock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO livestock_production (user_id, animal_type, breed, count, health_status)
        VALUES (?, ?, ?, ?,  ?)
    """, (
        livestock["user_id"], livestock["animal_type"], livestock["breed"],
        livestock["count"],  livestock["health_status"]
    ))
    conn.commit()
    conn.close()
    return {"message": "Livestock added successfully"}

def get_livestock_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livestock_production WHERE user_id = ?", (user_id,))
    livestock = cursor.fetchall()
    conn.close()
    return [dict(l) for l in livestock]






# ----------------------------
# SELLER MARKET LINK Helpers
# ----------------------------
def get_all_seller_market_links():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seller_market_link")
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip([d[0] for d in cursor.description], row)) for row in rows]

def get_seller_market_link_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seller_market_link WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip([d[0] for d in cursor.description], row)) for row in rows]

def add_seller_market_link(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO seller_market_link (
            user_id, market_name, seller_type, product_categories, available_equipment,
            payment_terms, equipment_status, farmer_preference_reason, latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("user_id"),
        data.get("market_name"),
        data.get("seller_type"),
        data.get("product_categories"),
        data.get("available_equipment"),
        data.get("payment_terms"),
        data.get("equipment_status"),
        data.get("farmer_preference_reason"),
        data.get("latitude"),
        data.get("longitude"),
    ))
    conn.commit()
    conn.close()
    return {"message": "Seller market link added successfully"}


# ----------------------------
# FARM BUDGET Helpers
# ----------------------------
def get_all_farm_budgets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farm_budget")
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip([d[0] for d in cursor.description], row)) for row in rows]

def get_farm_budget_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farm_budget WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip([d[0] for d in cursor.description], row)) for row in rows]

def add_farm_budget(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO farm_budget (
            user_id, available_budget_in_inr, credit_limit_in_inr, current_debt_in_inr,
            risk_appetite, past_trade_performance, equipment_ownership,
            logistics_capability, investment_flexibility
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("user_id"),
        data.get("available_budget_in_inr"),
        data.get("credit_limit_in_inr"),
        data.get("current_debt_in_inr"),
        data.get("risk_appetite"),
        data.get("past_trade_performance"),
        data.get("equipment_ownership"),
        data.get("logistics_capability"),
        data.get("investment_flexibility"),
    ))
    conn.commit()
    conn.close()
    return {"message": "Farm budget added successfully"}
