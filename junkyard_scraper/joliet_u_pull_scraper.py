from bs4 import BeautifulSoup
import requests
import io
import pandas as pd
import re

def is_year_present(pattern):
    # print('(is_year_present) patterm:', pattern)
    return True if re.findall(r"^\d{2}\s|^\d{4}\s", pattern) else False

def get_car_year(pattern):
    desired_car_year = re.findall(r"^\d{2}\s|^\d{4}\s", pattern)[0].strip()
    # print(f'get_car_year({pattern}) desired_car_year:', len(desired_car_year))
    desired_car_year = desired_car_year if len(desired_car_year) == 4 else f"20{desired_car_year}"
    return desired_car_year

class JunkyardScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        self.results = ""
        self.cached_results = []
        self.row_headers = []
    

    def valid_query(self, query):
        car_queries = query.strip().split(',')
        for request in car_queries:
            if len(request.strip().split(' ')) > 3:
                return False
        return True

# Chevrolet Tahoe, GMC Yukon, Cadillac Escalade, Chevrolet Silverado, GMC Sierra, Chevrolet Avalanche, Chevrolet Suburban, GMC Yukon XL, Chevrolet TrailBlazer, GMC Envoy, Buick Rainier, Saab 9-7X, Isuzu Ascender, Hummer H3, Chevrolet Colorado, GMC Canyon

    def set_results(self, results):
        self.results = results
        print(f'\n\n{self.results} \n\n')


    def cache_result(self, result):
        self.cached_results.append(result)


    # maps input string to dictionary of cars            
    def parse_queries(self, query):
        if not self.valid_query(query):
            return False
        
        queries = []
        for car in query.strip().split(','):
            car_search = car.strip().split(' ')
            year = ''
            if is_year_present(car):
                year = get_car_year(car)
                make = car_search[1].upper()
                car_search.pop(0)
            else:
                make = car_search[0].upper()

            if len(car_search) == 1:
                model = ''

            elif len(car_search) == 2:
                model = car_search[1].upper()

            elif len(car_search) == 3:
                model_first_value = car_search[1].upper()
                model_second_value = car_search[2].upper()
                model = model_first_value + '+' + model_second_value
            else:
                return False

            queries.append({'make': make, 'model': model, 'year': year})
        # print(f'parse_queries({query}): {queries}')
        return queries

   
    def fetch_junkyard_data(self, make='', model='',year='', ignore_headers=False):
        url = f'https://www.jolietupullit.com/inventory/?make={make}&model={model}'
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find(id="cars-table")

        if not table or not table.find(['td']):
            print(f"[!] Could not find {make} {model}'s")
            return ''
        
        rows = table.find_all('tr')
        if ignore_headers:
            #Skip the header row
            rows = rows[1:]
        
        return self.parse_table(rows,year)

    
    def parse_table(self, rows, year='', mode='csv'):
        if mode != 'csv':
            raise ValueError("Only CSV mode is currently supported.")
        
        data = ''
        for i, row in enumerate(rows):
            cells = row.find_all(['th', 'td'])
            cols = [cell.get_text(strip=True) for cell in cells]
            if i == 0 and row.find('th'):
                self.row_headers = cols
                data = ','.join(cols) + '\n'
            elif len(cols) >= 6:
                if (year and cols[0] == year) or not year:
                    data += ','.join(cols[:6]) + '\n'
        return data

    
    def fetch_results(self, query):
        parsed = self.parse_queries(query)
        if not parsed:
            print("[!] Invalid query format.")
            return ''

        for i, car in enumerate(parsed):
            self.results += self.fetch_junkyard_data(
                car['make'], car['model'], car['year'], ignore_headers=(i > 0)
            )
        self.set_results(self.results)
        self.cache_result(self.results)
        return self.results

    
    def display_options(self, options, numbers_on=True):
        for i, opt in enumerate(options):
            print(f"  [{i}] {opt}" if numbers_on else f"  -`{opt}`")

        print('\n')

    
    def car_selection(self):
        print("\nSearching Joliet U-Pull-It...\n")
        car = input("Enter make and model: ")
        if car.lower() == 'exit':
            print("Goodbye")
            return False
        #print(f"[car_selection] Valid query: {self.valid_query(car)}")
        
        return True if self.fetch_results(car) else False

    
    def opt_selection(self):
        callbacks = {
            'Sort Cars': self.handle_sort_by,
            'Filter Cars': self.handle_filter,
            'Search Again': self.handle_search,
        }
        #print(f'[opt_selection] len cacched_results: {len(self.cached_results)}')
        print("Actions:")
        if len(self.cached_results) > 1:
            callbacks['Go Back'] = self.handle_go_back

        opts = list(callbacks.keys())
        self.display_options(opts, numbers_on=True)
        choice = input(f"What next? (0-{len(opts)-1}): ")
        if choice.isdigit() and int(choice) in range(len(opts)):
            callbacks[opts[int(choice)]]()
            return True
        return False


    def filter_selection(self):
        print("\nFilter using headers:")
        opts = self.row_headers

        self.display_options(opts,numbers_on=False)
        choice = input(f"Filter By What (Write Query)?: ")
        if choice.lower() == 'exit':
            return False
        
        df = self.parse_df()
        filtered_df = self.handle_df(df,filter_query=choice, mode='filter')
        self.set_results(filtered_df)
        self.cache_result(filtered_df)
        return True


    def sort_selection(self):
        print("\nSorting through inventory")
        opts = self.row_headers
        self.display_options(opts,numbers_on=True)
        choice = input(f"Sort By What? [0-{len(opts)-1}]: ")
        if choice.lower() == 'exit':
            return True
        if choice.isdigit() and int(choice) in range(len(opts)):
            opt = opts[int(choice)]
            df = self.parse_df()
            sorted_df = self.handle_df(df,header_name=opt,mode='sort')
            self.set_results(sorted_df)
            self.cache_result(sorted_df)
            return True


    def handle_search(self):
        self.results = ''
        if(self.ask_input(self.car_selection)):
            self.handle_opts()
        else:
            print("Goodbye")

    #Returns results string to previous version
    def handle_go_back(self):
        print("\n Undoing last operation")
        #Remove last known results data
        self.cached_results.pop()
        #Sets results = previous cached results
        self.set_results(self.cached_results[-1])
        #Prompt for next steps
        self.ask_input(self.opt_selection)


    def handle_opts(self):
        self.ask_input(self.opt_selection)


    def parse_df(self):
        if (self.results):
            data_io = io.StringIO(self.results)
            df = pd.read_csv(data_io)
            return df


    def handle_df(self,dataframe,header_name=None,filter_query='',mode='sort'):
        if mode == 'filter':
            df = dataframe.query(filter_query)
        elif mode == 'sort':
            df = dataframe.sort_values(header_name)
        else:
            pass
        df = df.to_csv(index=False)
        return df


    def handle_sort_by(self):
        if(self.results):
            if(self.ask_input(self.sort_selection)):
                self.ask_input(self.opt_selection)
        else:
            print("[!] There aren't any results to sort. \n")

    
    def handle_filter(self, retries=3):
        if(self.results):
            try:
                if(self.ask_input(self.filter_selection)):
                    self.ask_input(self.opt_selection)
            except Exception as e:
                print('Try Again\n')
                self.handle_filter(retries=retries-1)         

    
    def ask_input(self, func):
        stop = func()
        #print(f'[ask_input] func:{func} , stop is :{stop}')
        while not stop:
            pass

        return True

# Run it
if __name__ == "__main__":
    scraper = JunkyardScraper()
    scraper.handle_search()
