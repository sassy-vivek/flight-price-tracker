from flask import Flask, request, jsonify
from scraper_amadeus import get_amadeus_price
from flask_cors import CORS

# -------------------------------------
# Flask Setup
# -------------------------------------
app = Flask(__name__)
CORS(app)

import os
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


@app.route("/search", methods=["GET"])
def search_flights():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    date = request.args.get("date")
    passengers = request.args.get("passengers", 1)

    # Fetch price from Amadeus
    best_price, offers = get_amadeus_price(
        origin, destination, date, passengers,
        CLIENT_ID, CLIENT_SECRET
    )

    if best_price == 0:
        return jsonify({
            "status": "error",
            "message": "No flights found."
        })

    # -------------------------------------
    # PRICE DROP ALERT SYSTEM
    # -------------------------------------
    try:
        # Load previous saved price
        with open("last_price.txt", "r") as f:
            last_price = int(f.read().strip())
    except:
        last_price = None  # first time running

    # Save current price
    with open("last_price.txt", "w") as f:
        f.write(str(best_price))

    # Send Telegram alert ONLY if price dropped
    if last_price and best_price < last_price:
        drop = last_price - best_price
        from alerts import send_telegram_alert
        send_telegram_alert(
            f"✈ <b>Price Drop Alert!</b>\n"
            f"{origin} → {destination}\n"
            f"Date: {date}\n"
            f"New Price: ₹{best_price}\n"
            f"Previous: ₹{last_price}\n"
            f"Drop: ₹{drop}",
            bot_token=BOT_TOKEN,
            chat_id=CHAT_ID
        )

    # -------------------------------------
    # Building Response for Frontend
    # -------------------------------------
    result = []
    for offer in offers[:5]:
        segment = offer["itineraries"][0]["segments"][0]

        result.append({
            "price": offer["price"]["total"],
            "airline": segment["carrierCode"],
            "flight_number": segment["number"],
            "from": segment["departure"]["iataCode"],
            "to": segment["arrival"]["iataCode"],
            "departure_time": segment["departure"]["at"],
            "arrival_time": segment["arrival"]["at"]
        })

    return jsonify({
        "best_price": best_price,
        "options": result
    })


# -------------------------------------
# Run Flask Backend
# -------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
