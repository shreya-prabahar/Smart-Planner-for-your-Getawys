from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# MONGODB CONNECTION
# ==========================================

client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["smart_planner"]

users = db["users"]
destinations = db["destinations"]
itineraries = db["itineraries"]
expenses = db["expenses"]
restaurant_bookings = db["restaurant_bookings"]


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return jsonify({
        "message": "Smart Planner for Your Getaways API is running!"
    })


# ==========================================
# USER REGISTRATION
# ==========================================

@app.route("/register", methods=["POST"])
def register():

    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "error": "All fields are required"
        }), 400

    if users.find_one({"email": email}):
        return jsonify({
            "error": "User already exists"
        }), 409

    user = {
        "name": name,
        "email": email,
        "password": password
    }

    result = users.insert_one(user)

    return jsonify({
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }), 201


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    user = users.find_one({
        "email": email,
        "password": password
    })

    if not user:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    return jsonify({
        "message": "Login successful",
        "user_id": str(user["_id"]),
        "name": user["name"]
    })


# ==========================================
# ADD DESTINATION
# ==========================================

@app.route("/destinations", methods=["POST"])
def add_destination():

    data = request.json

    destination = {
        "name": data.get("name"),
        "state": data.get("state"),
        "description": data.get("description"),
        "location": data.get("location"),
        "image": data.get("image"),
        "popular_places": data.get("popular_places", [])
    }

    result = destinations.insert_one(destination)

    return jsonify({
        "message": "Destination added successfully",
        "destination_id": str(result.inserted_id)
    }), 201


# ==========================================
# GET DESTINATIONS
# ==========================================

@app.route("/destinations", methods=["GET"])
def get_destinations():

    data = list(destinations.find())

    for destination in data:
        destination["_id"] = str(destination["_id"])

    return jsonify(data)


# ==========================================
# CREATE ITINERARY
# ==========================================

@app.route("/itinerary", methods=["POST"])
def create_itinerary():

    data = request.json

    itinerary = {
        "user_id": data.get("user_id"),
        "destination": data.get("destination"),
        "start_date": data.get("start_date"),
        "end_date": data.get("end_date"),
        "activities": data.get("activities", []),
        "notes": data.get("notes", [])
    }

    result = itineraries.insert_one(itinerary)

    return jsonify({
        "message": "Itinerary created successfully",
        "itinerary_id": str(result.inserted_id)
    }), 201


# ==========================================
# GET USER ITINERARIES
# ==========================================

@app.route("/itinerary/<user_id>", methods=["GET"])
def get_itinerary(user_id):

    data = list(itineraries.find({
        "user_id": user_id
    }))

    for itinerary in data:
        itinerary["_id"] = str(itinerary["_id"])

    return jsonify(data)


# ==========================================
# ADD EXPENSE
# ==========================================

@app.route("/expenses", methods=["POST"])
def add_expense():

    data = request.json

    expense = {
        "user_id": data.get("user_id"),
        "category": data.get("category"),
        "amount": float(data.get("amount")),
        "description": data.get("description"),
        "date": datetime.now()
    }

    result = expenses.insert_one(expense)

    return jsonify({
        "message": "Expense added successfully",
        "expense_id": str(result.inserted_id)
    }), 201


# ==========================================
# GET USER EXPENSES
# ==========================================

@app.route("/expenses/<user_id>", methods=["GET"])
def get_expenses(user_id):

    data = list(expenses.find({
        "user_id": user_id
    }))

    total = 0

    for expense in data:
        expense["_id"] = str(expense["_id"])
        expense["date"] = expense["date"].strftime("%Y-%m-%d")
        total += expense["amount"]

    return jsonify({
        "expenses": data,
        "total_expense": total
    })


# ==========================================
# RESTAURANT BOOKING
# ==========================================

@app.route("/restaurant-booking", methods=["POST"])
def restaurant_booking():

    data = request.json

    booking = {
        "user_id": data.get("user_id"),
        "restaurant_name": data.get("restaurant_name"),
        "location": data.get("location"),
        "booking_date": data.get("booking_date"),
        "booking_time": data.get("booking_time"),
        "number_of_people": data.get("number_of_people"),
        "status": "Confirmed"
    }

    result = restaurant_bookings.insert_one(booking)

    return jsonify({
        "message": "Restaurant booked successfully",
        "booking_id": str(result.inserted_id),
        "status": "Confirmed"
    }), 201


# ==========================================
# GET RESTAURANT BOOKINGS
# ==========================================

@app.route("/restaurant-booking/<user_id>", methods=["GET"])
def get_bookings(user_id):

    data = list(
        restaurant_bookings.find({
            "user_id": user_id
        })
    )

    for booking in data:
        booking["_id"] = str(booking["_id"])

    return jsonify(data)


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
