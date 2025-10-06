import os
import time
from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

def scrape_amazon_multiple_pages(base_url, myProductArray, max_pages=2):
    all_results = []

    # Chrome options for headless deployment
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for page in range(1, max_pages + 1):
        print(f"🔍 Scraping Page {page}...")
        url = f"{base_url}&page={page}"
        driver.get(url)
        time.sleep(3)

        for _ in range(2):
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight/2);")
            time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.select("div.s-main-slot div.s-result-item[data-asin]")

        for item in items:
            asin = item.get('data-asin')
            if asin and asin in myProductArray:
                title_elem = item.select_one("h2")
                title = title_elem.get_text(strip=True) if title_elem else "N/A"
                rating_elem = item.select_one("span.a-icon-alt")
                rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"
                review_elem = item.select_one("span.a-size-base.s-underline-text")
                review_count = review_elem.get_text(strip=True) if review_elem else "N/A"
                sponsored_elem = item.select_one("span.s-label-popover-default")
                sponsored = sponsored_elem.get_text(strip=True) if sponsored_elem else "No"

                all_results.append({
                    "ASIN": asin,
                    "Title": title,
                    "Rating": rating,
                    "Review Count": review_count,
                    "Sponsored": sponsored
                })

    driver.quit()
    return all_results


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
        scraped_products = scrape_amazon_multiple_pages(url, myProductArray, max_pages=1)
        unique = {p["ASIN"]: p for p in scraped_products}
        results[name] = list(unique.values())

    return jsonify(results)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
