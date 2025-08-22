import json
import requests
import time
import logging

PRODUCTS_FILE = "products.json"
ZIPCODE = "560085"
CHECK_INTERVAL = 10  # seconds

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

def check_croma_availability(item_id: str, zip_code: str) -> bool:
    url = "https://api.croma.com/inventory/oms/v2/tms/details-pwa/"
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://www.croma.com",
        "referer": "https://www.croma.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    payload = {
        "promise": {
            "allocationRuleID": "SYSTEM",
            "checkInventory": "Y",
            "organizationCode": "CROMA",
            "sourcingClassification": "EC",
            "promiseLines": {
                "promiseLine": [
                    {
                        "fulfillmentType": "HDEL",
                        "mch": "",
                        "itemID": str(item_id),
                        "lineId": "1",
                        "categoryType": "nonMobile",
                        "reEndDate": "2500-01-01",
                        "reqStartDate": "",
                        "requiredQty": "1",
                        "shipToAddress": {
                            "company": "",
                            "country": "",
                            "city": "",
                            "mobilePhone": "",
                            "state": "",
                            "zipCode": str(zip_code),
                            "extn": {
                                "irlAddressLine1": "",
                                "irlAddressLine2": ""
                            }
                        },
                        "extn": {
                            "widerStoreFlag": "N"
                        }
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        promise_lines = (
            data.get("promise", {})
                .get("suggestedOption", {})
                .get("option", {})
                .get("promiseLines", {})
                .get("promiseLine", [])
        )
        return len(promise_lines) > 0

    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            logging.warning(f"403 Forbidden for item {item_id}. Possible block, rate limit, or authentication required.")
        else:
            logging.error(f"HTTP error for item {item_id}: {e}")
        return False
    except requests.exceptions.RequestException as e:
        logging.warning(f"Request error for item {item_id}: {e}")
        return False
    except Exception as e:
        logging.error(f"Error for item {item_id}: {e}")
        return False

def load_products():
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)

def check_all_stock(zip_code):
    products = load_products()
    for product in products:
        if not product.get("enabled", False):
            continue
        item_id = product["id"]
        name = product["name"]
        in_stock = check_croma_availability(item_id=item_id, zip_code=zip_code)
        if in_stock:
            logging.info(f"✅ In stock: {name} (ID: {item_id}) for Pincode: {zip_code}")
        else:
            logging.info(f"❌ Out of stock: {name} (ID: {item_id}) for Pincode: {zip_code}")

if __name__ == "__main__":
    try:
        while True:
            check_all_stock(zip_code=ZIPCODE)
            logging.info("CHECKED ALL\n")
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Script stopped by user.")
