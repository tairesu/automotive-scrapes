import requests
from bs4 import BeautifulSoup


class LKQSearch():
    def __init__(self):
        self.results = []
        self.base_url = "https://www.lkqpickyourpart.com/DesktopModules/pyp_vehicleInventory/getVehicleInventory.aspx"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://www.lkqpickyourpart.com/inventory/blue-island-1582/",
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }
        self.params = {}


    def fetch_inventory(self, filter, store_id=1582):
        page_number = 1
        #While valid page exists 
        while(self.is_page_valid(page_number, filter, store_id)):
            page_number += 1
        self.display(self.results)
        return self.results


    def is_page_valid(self, page_number,filter,store_id):
        vehicle_cards = self.fetch_inventory_html(page_number, filter, store_id)
        print(f'[is_page_valid] Page #{page_number} has data') if len(vehicle_cards) > 0 else print(f'[is_page_valid] Page #{page_number} has NO data')
        return len(vehicle_cards) > 0


    def fetch_inventory_html(self, page_number,filter,store_id):
        self.params = {
            "page": page_number,
            "filter": filter,
            "store": store_id
        }
        response = requests.get(self.base_url, headers=self.headers, params=self.params)
        soup = BeautifulSoup(response.text, "html.parser")
        vehicle_cards = soup.find_all(class_="pypvi_resultRow")
        if len(vehicle_cards) > 1:
            self.handle_vehicle_cards_html(vehicle_cards)
        return vehicle_cards


    def handle_vehicle_cards_html(self, vehicle_cards=[]):
        for card in vehicle_cards:
            vehicle_data = self.parse_card_html(card)
            self.results.append(vehicle_data)


    # Take in raw vehicle card HTML and format it to a dictionary
    def parse_card_html(self,card_html) :
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
                    field_name = item.get_text(strip=True).replace(':','').lower().strip()
                    inventory_car[field_name] = item.next_sibling.strip()
            elif len(items) == 1:
                field_name = items[0].get_text().replace(':','').lower().strip()
                item_value = items[0].next_sibling.strip()
                if('available' in field_name):
                    item_value = detail.find('time').get_text()
                inventory_car[field_name] = item_value
        return inventory_car


    def display(self, results):
        print('\n')
        print('Year, Make, Model, Row, Space, Color, VIN, Stock#, EntryDate')
        for result in results:
            print(f"{result['year']}, {result['make']}, {result['model']}, {result['row']}, {result['space']}, {result['color']},{result['vin']}, {result['stock #']}, {result['available']}")


# Example usage:
yardSearch = LKQSearch()
yardSearch.fetch_inventory("tahoe")

