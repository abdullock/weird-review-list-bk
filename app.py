from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os

app = Flask(__name__)
CORS(app)

def scrape_amazon_multiple_pages(base_url, myProductArray, max_pages=2):
    all_results = []

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment for headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for page in range(1, max_pages + 1):
        url = f"{base_url}&page={page}"
        driver.get(url)
        time.sleep(3)

        # Scroll to load products
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight/3);")
            time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.select("div.s-main-slot div.s-result-item[data-asin]")

        if not items:
            continue

        for item in items:
            asin = item.get('data-asin')
            if not asin or asin not in myProductArray:
                continue

            title_elem = item.select_one("h2 span.a-text-normal")
            rating_elem = item.select_one("span.a-icon-alt")
            review_elem = item.select_one("span.a-size-base.s-underline-text")
            sponsored_elem = item.select_one("span.s-label-popover-default")

            all_results.append({
                "Index": item.get('data-index', 'N/A'),
                "ASIN": asin,
                "Title": title_elem.get_text(strip=True) if title_elem else "N/A",
                "Rating": rating_elem.get_text(strip=True) if rating_elem else "N/A",
                "Review Count": review_elem.get_text(strip=True) if review_elem else "N/A",
                "Sponsored": sponsored_elem.get_text(strip=True) if sponsored_elem else "No"
            })

        time.sleep(2)

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
        scraped_products = scrape_amazon_multiple_pages(url, myProductArray, max_pages=2)
        unique_products = {p["ASIN"]: p for p in scraped_products}
        results[name] = list(unique_products.values())

    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
