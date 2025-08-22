import json
import requests
import time


PRODUCTS_FILE = "products.json"
ZIPCODE = "560085"

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

        # Success → promiseLine list is non-empty
        promise_lines = (
            data.get("promise", {})
                .get("suggestedOption", {})
                .get("option", {})
                .get("promiseLines", {})
                .get("promiseLine", [])
        )
        
        return len(promise_lines) > 0

    except Exception as e:
        print(f"Error for item {item_id}: {e}")
        return False


def check_all_stock(zip_code):
    # Load products.json
    with open(PRODUCTS_FILE, "r") as f:
        products = json.load(f)

    # Iterate over products
    for product in products:
        if not product.get("enabled", False):
            continue  # skip disabled products

        item_id = product["id"]
        name = product["name"]

        in_stock = check_croma_availability(item_id=item_id, zip_code=zip_code)
        if in_stock:
            print(f"✅ In stock: {name} (ID: {item_id}) for Pincode: {zip_code}")
        else:
            print(f"❌ Out of stock: {name} (ID: {item_id}) for Pincode: {zip_code}")


if __name__ == "__main__":
    while 1:
        check_all_stock(zip_code=ZIPCODE)
        print("CHECKED ALL\n")
        time.sleep(10)
