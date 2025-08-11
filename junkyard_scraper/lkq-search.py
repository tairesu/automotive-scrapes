import requests
from bs4 import BeautifulSoup


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.lkqpickyourpart.com/inventory/blue-island-1582/",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9"
    }

base_url = "https://www.lkqpickyourpart.com/DesktopModules/pyp_vehicleInventory/getVehicleInventory.aspx"

# Take in raw vehicle card HTML and format it to a dictionary
def parse_card_html(card_html) :
    inventory_car = {}
    year_make_model = card_html.find(class_="pypvi_ymm").get_text(' ', strip=True)
    inventory_car['year'] = year_make_model.split(' ')[0]
    inventory_car['make'] = year_make_model.split(' ')[1]
    inventory_car['model'] = year_make_model.split(' ')[2]
    details = card_html.find_all(class_="pypvi_detailItem")
    #loop through each detail item (color, stock, available inventory_car, etc)
    for detail in details:
        items = detail.find_all('b')
        if len(items) > 1:
            for item in items:
                field_name = item.get_text(strip=True)
                inventory_car[field_name] = item.next_sibling.strip()
        elif len(items) == 1:
            field_name = items[0].get_text()
            item_value = items[0].next_sibling.strip()
            if('Available' in field_name):
                item_value = detail.find('time').get_text()
            inventory_car[field_name] = item_value
    return inventory_car


def fetch_inventory_html(page_number,filter,store_id):
    params = {
        "page": page_number,
        "filter": filter,
        "store": store_id
    }
    response = requests.get(base_url, headers=headers, params=params)
    soup = BeautifulSoup(response.text, "html.parser")
    vehicle_cards = soup.find_all(class_="pypvi_resultRow")
    return vehicle_cards


def is_page_valid(page_number,filter,store_id):
    vehicle_cards = fetch_inventory_html(page_number, filter, store_id)
    print(f'[is_page_valid] Page #{page_number} has data') if len(vehicle_cards) > 0 else print(f'[is_page_valid] Page #{page_number} has NO data')
    return len(vehicle_cards) > 0


def fetch_inventory(filter, store_id=1582):
    page_number = 1
    results = []
    #While valid page exists 
    while(is_page_valid(page_number, filter, store_id)):
        vehicle_cards = fetch_inventory_html(page_number, filter, store_id)
        if not vehicle_cards:
            print(soup)
            print(f"Page {page}: No more vehicles.")
            break

        for card in vehicle_cards:
            vehicle_data = parse_card_html(card)
            results.append(vehicle_data)
        page_number += 1
    return results

# Example usage:
vehicles = fetch_inventory("civic")
print(f"{len(vehicles)} Found")
for v in vehicles:
    print(v)
