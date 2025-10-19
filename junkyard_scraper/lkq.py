import requests
from bs4 import BeautifulSoup
import re

class Search():
    def __init__(self, query):
        self.query = query.strip()
        self.results = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        
    def is_year_present(self) -> bool:
    # print('(is_year_present) patterm:', pattern)
        text = self.query.replace('–', '-').replace('—', '-')
        return True if re.findall(r"^\d{2}\s|^\d{4}\s", text) else False

    def is_year_range_present(self) -> bool:
        text = self.query.replace('–', '-').replace('—', '-')
        return True if re.findall(r"^(\d{2}-\d{2}\s)|^(\d{4}-\d{4}\s)", text) else False
    
    def extract_year(self) -> str:
        if not self.is_year_present:
            raise ValueError('Year needs to be present for extraction')
        text = self.query.replace('–', '-').replace('—', '-')
        try: 
            desired_car_year = re.findall(r"^\d{2}\s|^\d{4}\s", text)[0].strip()
        except IndexError:
            raise ValueError(f'Cannot extract year from query:{self.query}')
            
        # print(f'extract_year({self}) desired_car_year:', len(desired_car_year))
        desired_car_year = desired_car_year if len(desired_car_year) == 4 else f"20{desired_car_year}"
        return desired_car_year 

    def extract_year_range(self) -> tuple:
        if not self.is_year_range_present:
            raise ValueError('Car Year range needs to be present for extraction')
        
        text = self.query.replace('–', '-').replace('—', '-')
        try:
            range_str = re.findall(r"^\d{2}-\d{2}|^\d{4}-\d{4}", text.strip())[0]
            min_year = range_str.split('-')[0]
            max_year = range_str.split('-')[1]
        except IndexError:
            raise ValueError(f'Cannot extract car_year_range from query: {self.query}')
        
        min_year = "20" + min_year if len(min_year) == 2 else min_year
        max_year = "20" + max_year if len(max_year) == 2 else max_year
        return (min_year, max_year)
    
    def extract_conditionals(self) -> tuple:
        conditionals = {}
        semantics = self.query.split(' ')
        
        if self.is_year_present:
            conditionals['year'] = self.extract_year()
            semantics.pop(0)
        elif not self.is_year_present and self.is_year_range_present:
            conditionals['minYear'], conditionals['maxYear'] = self.extract_year_range()
            semantics.pop(0)
        cleaned_query = ' '.join(semantics)
        return conditionals, cleaned_query
    
    def get_results(self, output='dict'):
        if not self.results:
            return ''

        if output == 'dict':
            return self.results
        elif output == 'csv':
            return self.results_csv
    
    
class LKQSearch(Search):
    """
    Represents a search on the LKQ junkyard data
    
    Attributes:
        query (str): The raw search query in string form.
        results (list): Holds the inventory data.
        yard_info (dict): Metadata about the yard itself.
        base_url (str): URL holding the inventory data.
        headers (dict): Content headers for web scraping.
        params (dict):  URL parameters for requesting site data  
    """
    
    def __init__(self, query):
        """
        Initializes search instance
        
        Args: 
            querys (str): The raw search query 
        """
        super().__init__(query)
        self.yard_info = {'name': 'LKQ (Blue island)'}
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
        #self.handle_query(self.query)
        
    def handle_query(self):
        querys_list = self.query.split(',')
        #Loop through that array..
        for query in querys_list:
            #capture the year/year range conditionals
            conditionals, cleaned_query = super().extract_conditionals()
            #... grab matching vehicles from online inventory that matches the query, and satisfies the conditional 
            self.fetch_inventory(query=cleaned_query, conditionals=conditionals)
        

    def fetch_inventory(self, query, store_id=1582,conditionals={}):
        page_number = 1
        #While valid page exists 
        while(self.is_page_valid(page_number, query, store_id, conditionals)):
            page_number += 1
        return self.results


    def is_page_valid(self, page_number,query,store_id, conditionals={}) -> bool:
        # Grabs all divs HTML 
        vehicle_cards = self.fetch_inventory_html(page_number, query, store_id, conditionals)
        return len(vehicle_cards) > 0


    def fetch_inventory_html(self, page_number,query,store_id, conditionals={}) -> list:
        self.params = {
            "page": page_number,
            "filter": query,
            "store": store_id
        }
        response = requests.get(self.base_url, headers=self.headers, params=self.params)
        soup = BeautifulSoup(response.text, "html.parser")
        vehicle_cards = soup.find_all(class_="pypvi_resultRow")
        if len(vehicle_cards) > 1:
            self.handle_vehicle_cards_html(vehicle_cards, conditionals)
        return vehicle_cards


    def handle_vehicle_cards_html(self, vehicle_cards=[], conditionals={}):
        for card in vehicle_cards:
            vehicle_data = self.extract_card_html(card)
            if self.satisfies_conditionals(vehicle_data, conditionals):
                self.results.append(vehicle_data)

    def satisfies_conditionals(self, vehicle_data, conditionals={}) -> bool:
        vehicle_matches_year = ('year' in conditionals.keys() and vehicle_data['year'] == conditionals['year'])
        vehicle_in_year_range = ('minYear' in conditionals.keys() and int(vehicle_data['year']) in range(int(conditionals['minYear']), int(conditionals['maxYear']) + 1))
        ignore_year_and_range = (len(conditionals.keys()) == 0)
        if(vehicle_matches_year or vehicle_in_year_range or ignore_year_and_range):
            return True
        return False


    # Turns matching vehicle card HTML and formats the content into a dictionary
    def extract_card_html(self,card_html) -> dict:
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
        print('|',self.yard_info['name'])
        print('\n')
        print('Year, Make, Model, Row, Space, Color, VIN, Stock#, EntryDate')
        for result in self.results:
            print(f"{result['year']}, {result['make']}, {result['model']}, {result['row']}, {result['space']}, {result['color']},{result['vin']}, {result['stock #']}, {result['available']}")
    

# Example usage:
if __name__ == '__main__':
    stop = False
    while(stop != True):
        query = input('\nEnter year, make, model: ')
        if query.strip().lower() in ['stop','halt','exit']:
            stop = True

        yardSearch = LKQSearch(query)
        yardSearch.display_data()


