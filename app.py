# amazonScraping.py
from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

def scrape_amazon(base_url, myProductArray, max_pages=2):
    all_results = []

    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")
        url = f"{base_url}&page={page}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Failed to fetch {url}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select("div.s-main-slot div.s-result-item[data-asin]")

            for item in items:
                asin = item.get("data-asin")
                if not asin or asin not in myProductArray:
                    continue

                title_elem = item.select_one("h2 span.a-text-normal")
                rating_elem = item.select_one("span.a-icon-alt")
                review_elem = item.select_one("span.a-size-base.s-underline-text")
                sponsored_elem = item.select_one("span.s-label-popover-default")

                all_results.append({
                    "ASIN": asin,
                    "Title": title_elem.get_text(strip=True) if title_elem else "N/A",
                    "Rating": rating_elem.get_text(strip=True) if rating_elem else "N/A",
                    "Review Count": review_elem.get_text(strip=True) if review_elem else "N/A",
                    "Sponsored": sponsored_elem.get_text(strip=True) if sponsored_elem else "No"
                })
        except Exception as e:
            print(f"Error scraping page {page}: {e}")

    # Remove duplicates by ASIN
    unique_products = {p["ASIN"]: p for p in all_results}
    return list(unique_products.values())

# ---------------- FLASK ROUTE ---------------- #
@app.route("/scrape_all", methods=["GET"])
def scrape_all():
    urls = {
        "study_lamp": "https://www.amazon.in/s?k=lamp+for+study+room",
        "insect_killer": "https://www.amazon.in/s?k=insect+killer+machine+for+office",
        "mosquito_bat": "https://www.amazon.in/s?k=mosquito+bat+with+uv+light"
    }

    myProductArray = [
        "B0F4MWK1PQ", "B0F4MZBC74", "B0F9Y8TDZW", "B0F9Y3RBL5",
        "B0F678285F", "B0FB8XG4Q4", "B0DSW6X4NW", "B0F9YZ7RTP",
        "B0DVZLJ8P9", "B0C3XV4CGJ", "B0DBF15R4Q", "B0CF598GJG",
        "B0DBDZ7CDS", "B0D7CZJ533", "B0CFLG25Y5", "B0DC3N2ZX3",
        "B0CJ52B5TK", "B0D8449YD5", "B0FCMV3DBM", "B0DFWBT7B9",
        "B0DFWF9R1P", "B0DFWDZ3B3", "B0DQ8WVMR6", "B0F5WX93PH",
        "B0FCMTL9ZZ", "B0BXT1HKF4", "B0CD2CTNNF", "B0DBZ1XVNT",
        "B0B919D52V", "B0D8Q3Z8QL", "B0FR9KHQZM"
    ]

    results = {}
    for name, url in urls.items():
        results[name] = scrape_amazon(url, myProductArray, max_pages=2)

    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
