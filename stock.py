import json
import requests
import time
import datetime

PRODUCTS_FILE = "products.json"
ZIPCODE = "560085"

def check_croma_availability(item_id: str, zip_code: str):
    """
    Returns:
      True  -> In stock
      False -> Out of stock
      None  -> Error (do not print)
    """
    url = "https://api.croma.com/inventory/oms/v2/tms/details-pwa/"
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://www.croma.com"
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
        if response.status_code != 200:
            print(f"⚠️ API returned status {response.status_code} for item {item_id}")
            return None

        try:
            data = response.json()
        except ValueError:
            print(f"⚠️ Invalid JSON response for item {item_id}")
            return None

        # Success → promiseLine list is non-empty
        promise_lines = (
            data.get("promise", {})
                .get("suggestedOption", {})
                .get("option", {})
                .get("promiseLines", {})
                .get("promiseLine", [])
        )
        
        return True if len(promise_lines) > 0 else False

    except Exception as e:
        print(f"⚠️ Error for item {item_id}: {e}")
        return None


def check_all_stock(zip_code):
    # Load products.json
    with open(PRODUCTS_FILE, "r") as f:
        products = json.load(f)

    print(f"\n=== Stock Check at {datetime.datetime.now()} ===")
    for product in products:
        if not product.get("enabled", False):
            continue  # skip disabled products

        item_id = product["id"]
        name = product["name"]

        result = check_croma_availability(item_id=item_id, zip_code=zip_code)
        if result is True:
            print(f"✅ In stock: {name} (ID: {item_id}) for Pincode: {zip_code}")
        elif result is False:
            print(f"❌ Out of stock: {name} (ID: {item_id}) for Pincode: {zip_code}")
        else:
            # None -> Error, skip printing stock status
            pass


if __name__ == "__main__":
    while True:
        check_all_stock(zip_code=ZIPCODE)
        print("CHECKED ALL\n")
        time.sleep(10)
