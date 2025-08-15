import requests
from bs4 import BeautifulSoup
import re

class LKQSearch():
    def __init__(self, filters, store_id='1582'):
        self.store = self.get_store_data(store_id)
        self.filters = filters
        self.results = []
        self.base_url = "https://www.lkqpickyourpart.com/DesktopModules/pyp_vehicleInventory/getVehicleInventory.aspx"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": f"https://www.lkqpickyourpart.com/inventory/blue-island-{store_id}/",
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }

        self.params = {}
        self.handle_filters(self.filters)
        
    def get_store_data(self, store_id):
        stores_data = {
            "1582": {"name": "LKQ Blue Island", "id": "1582"},
            "1585": {"name": "LKQ Chicago South", "id": "1585"},
            "1581": {"name": "LKQ Chicago", "id": "1581"},
        }
        return stores_data[store_id]


    def handle_filters(self, filters):
        #Parses the given filters into a comma separated array
        filters_list = self.parse_filters(filters)
        #Loop through that array..
        for filter in filters_list:
            #capture the year/year range conditionals
            conditionals, cleaned_filter = self.parse_filter_conditionals(filter.strip())
            #... grab matching vehicles from online inventory that matches the filter, and satisfies the conditional 
            self.fetch_inventory(filter=cleaned_filter, conditionals=conditionals)
        

    def parse_filters(self, filters):
        return filters.split(',')

    def parse_filter_conditionals(self, filter):
        conditionals = {}
        semantics = filter.strip().split(' ')
        
        if self.is_year_present(filter):
            conditionals['year'] = self.parse_car_year(filter)
            semantics.pop(0)
        elif not self.is_year_present(filter) and self.is_year_range_present(filter):
            conditionals['minYear'], conditionals['maxYear'] = self.parse_car_year_range(filter)
            semantics.pop(0)
        cleaned_filter = ' '.join(semantics)
        return conditionals, cleaned_filter


    def is_year_present(self, pattern):
    # print('(is_year_present) patterm:', pattern)
        text = pattern.replace('–', '-').replace('—', '-')
        return True if re.findall(r"^\d{2}\s|^\d{4}\s", text) else False

    def parse_car_year(self, pattern):
        text = pattern.replace('–', '-').replace('—', '-')
        desired_car_year = re.findall(r"^\d{2}\s|^\d{4}\s", text)[0].strip()
        # print(f'parse_car_year({pattern}) desired_car_year:', len(desired_car_year))
        desired_car_year = desired_car_year if len(desired_car_year) == 4 else f"20{desired_car_year}"
        return desired_car_year

    def is_year_range_present(self, pattern):
        text = pattern.replace('–', '-').replace('—', '-')
        return True if re.findall(r"^(\d{2}-\d{2}\s)|^(\d{4}-\d{4}\s)", text) else False

    def parse_car_year_range(self, pattern):
        text = pattern.replace('–', '-').replace('—', '-')
        range_str = re.findall(r"^\d{2}-\d{2}|^\d{4}-\d{4}", text.strip())[0]
        min_year = range_str.split('-')[0]
        max_year = range_str.split('-')[1]
        min_year = "20" + min_year if len(min_year) == 2 else min_year
        max_year = "20" + max_year if len(max_year) == 2 else max_year
        return (min_year, max_year)

    def fetch_inventory(self, filter,conditionals={}):
        page_number = 1
        #While valid page exists 
        while(self.is_page_valid(page_number, filter,  conditionals)):
            page_number += 1
        return self.results


    def is_page_valid(self, page_number,filter,conditionals={}):
        # Grabs all divs HTML 
        vehicle_cards = self.fetch_inventory_html(page_number, filter,  conditionals)
        return len(vehicle_cards) > 0


    def fetch_inventory_html(self, page_number,filter, conditionals={}):
        self.params = {
            "page": page_number,
            "filter": filter,
            "store": self.store['id']
        }
        response = requests.get(self.base_url, headers=self.headers, params=self.params)
        soup = BeautifulSoup(response.text, "html.parser")
        vehicle_cards = soup.find_all(class_="pypvi_resultRow")
        if len(vehicle_cards) > 1:
            self.handle_vehicle_cards_html(vehicle_cards, conditionals)
        return vehicle_cards


    def handle_vehicle_cards_html(self, vehicle_cards=[], conditionals={}):
        for card in vehicle_cards:
            vehicle_data = self.parse_card_html(card)
            if self.satisfies_conditionals(vehicle_data, conditionals):
                self.results.append(vehicle_data)

    def satisfies_conditionals(self, vehicle_data, conditionals={}):
        vehicle_matches_year = ('year' in conditionals.keys() and vehicle_data['year'] == conditionals['year'])
        vehicle_in_year_range = ('minYear' in conditionals.keys() and int(vehicle_data['year']) in range(int(conditionals['minYear']), int(conditionals['maxYear']) + 1))
        ignore_year_and_range = (len(conditionals.keys()) == 0)
        if(vehicle_matches_year or vehicle_in_year_range or ignore_year_and_range):
            return True
        return False


    # Turns matching vehicle card HTML and formats the content into a dictionary
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


    def display_data(self):
        if len(self.results) == 0:
            return ''

        print('\n')
        print('|',self.store['name'])
        print('\n')
        print('Year, Make, Model, Row, Space, Color, VIN, Stock#, EntryDate')
        for result in self.results:
            print(f"{result['year']}, {result['make']}, {result['model']}, {result['row']}, {result['space']}, {result['color']},{result['vin']}, {result['stock #']}, {result['available']}")
    
    def get_results(self, output='dict'):
        if not self.results:
            return ''

        if output == 'dict':
            return self.results
        elif output == 'csv':
            return self.results_csv

    def get_data(self):
        output_dict = self.store
        output_dict['summary'] = f'{len(self.results)} Vehicle(s) Found'
        output_dict['results'] = self.get_results()
        return output_dict

# Example usage:
if __name__ == '__main__':
    stop = False
    while(stop != True):
        filter = input('\nEnter year, make, model: ')
        if filter.strip().lower() in ['stop','halt','exit']:
            stop = True

        yardSearch = LKQSearch(filter,store_id='1582')
        yardSearch2 = LKQSearch(filter,store_id='1585')
        yardSearch2 = LKQSearch(filter,store_id='1581')
        yardSearch.display_data()
        yardSearch2.display_data()
        yardSearch3.display_data()


