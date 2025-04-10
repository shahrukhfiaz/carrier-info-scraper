from flask import Flask, request, jsonify
import requests
import re
import os
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/carrier", methods=["GET"])
def carrier_details():
    usdot = request.args.get("usdot")
    if not usdot:
        return {"error": "Missing USDOT number"}, 400

    url = f"https://ai.fmcsa.dot.gov/SMS/Carrier/{usdot}/CarrierRegistration.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://ai.fmcsa.dot.gov/",
        "Accept": "text/html"
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            return {
                "error": "Failed to fetch page",
                "status": res.status_code,
                "usdot": usdot
            }, 400

        soup = BeautifulSoup(res.text, "html.parser")
        carrier_info = {}

        ul_col1 = soup.find("ul", class_="col1")
        if not ul_col1:
            return {
                "usdot": usdot,
                "carrier_info": {},
                "message": "No carrier info found"
            }

        for li in ul_col1.find_all("li"):
            label = li.find("label")
            span = li.find("span", class_="dat")

            if label and span:
                key = label.get_text(strip=True).replace(":", "")
                value = span.get_text(separator=" ", strip=True).replace("\n", " ").replace("\r", "")
                carrier_info[key] = value

        return {
            "usdot": usdot,
            "carrier_info": carrier_info
        }

    except Exception as e:
        return {
            "error": "Exception during scraping",
            "details": str(e),
            "usdot": usdot
        }, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
