import requests
import base64

def get_amadeus_token(client_id, client_secret):
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def get_amadeus_price(origin, destination, date, passengers, client_id, client_secret):
    try:
        token = get_amadeus_token(client_id, client_secret)

        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"

        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": date,
            "adults": passengers,
            "currencyCode": "INR",
            "max": 10
        }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        offers = data.get("data", [])
        if not offers:
            return 0, None

        prices = []
        for offer in offers:
            price = float(offer["price"]["total"])
            prices.append(price)

        best_price = min(prices)

        return int(best_price), offers

    except Exception as e:
        print("Amadeus Error:", e)
        return 0, None
