from flask import Flask, request, jsonify
import requests
import re
import os

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
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return {
                "error": "Failed to fetch page",
                "status": res.status_code,
                "usdot": usdot
            }, 400

        html = res.text

        # Extract <td class="col1">...</td>
        matches = re.findall(r'<td\s+class="col1">([\s\S]*?)<\/td>', html, re.IGNORECASE)
        cleaned = [m.strip() for m in matches]

        return {
            "usdot": usdot,
            "col1_values": cleaned
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
