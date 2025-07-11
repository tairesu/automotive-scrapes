from bs4 import BeautifulSoup
import requests
import io
import pandas as pd

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
            if len(request.strip().split(' ')) > 2:
                return False
        return True

    def set_results(self, results):
        self.cached_results.append(self.results)
        self.results = results
        print(self.results)


    def parse_queries(self, query):
        if not self.valid_query(query):
            return False
        
        queries = []
        for car in query.strip().split(','):
            parts = car.strip().split(' ')
            make = parts[0].upper()
            model = parts[1].upper() if len(parts) == 2 else ''
            queries.append({'make': make, 'model': model})
        return queries

   
    def fetch_junkyard_data(self, make='', model='', ignore_headers=False):
        url = f'https://www.jolietupullit.com/inventory/?make={make}&model={model}'
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find(id="cars-table")

        if not table or not table.find(['td']):
            print(f"[!] Could not find {make} {model}'s")
            return ''
        
        rows = table.find_all('tr')
        if ignore_headers:
            rows = rows[1:]
        
        return self.parse_table(rows)

    
    def parse_table(self, rows, mode='csv'):
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
                data += ','.join(cols[:6]) + '\n'
        return data

    
    def fetch_results(self, query):
        parsed = self.parse_queries(query)
        if not parsed:
            print("[!] Invalid query format.")
            return ''

        print(f"[fetch_results] Parsed: {parsed}")
        for i, car in enumerate(parsed):
            self.results += self.fetch_junkyard_data(
                car['make'], car['model'], ignore_headers=(i > 0)
            )
        self.set_results(self.results)
        return self.results

    
    def display_options(self, options, numbers_on=True):
        for i, opt in enumerate(options):
            print(f"{i}: {opt}" if numbers_on else f"{opt}")

    
    def car_selection(self):
        print("Searching Joliet U-Pull-It...")
        car = input("Enter make and model: ")
        if car.lower() == 'exit':
            print("Goodbye")
            return False
        print(f"[car_selection] Valid query: {self.valid_query(car)}")
        
        return True if self.fetch_results(car) else False

    
    def opt_selection(self):
        callbacks = {
            'Sort Cars': self.handle_sort_by,
            'Filter Cars': self.handle_filter,
            'Search Again': self.handle_search,
        }
        
        opts = list(callbacks.keys())
        self.display_options(opts, numbers_on=True)
        choice = input(f"What next? (0-{len(opts)-1}): ")
        if choice.isdigit() and int(choice) in range(len(opts)):
            callbacks[opts[int(choice)]]()
            return True
        return False

    def filter_selection(self):
        opts = self.row_headers
        self.display_options(opts,numbers_on=False)
        choice = input(f"Filter By What (Write Query)?: ")
        if choice.lower() == 'exit':
            return False
        
        df = self.parse_df()
        filtered_df = self.handle_df(df,filter_query=choice, mode='filter')
        self.set_results(filtered_df)
        return True



    def handle_search(self):
        self.results = ''
        if(self.ask_input(self.car_selection)):
            self.handle_opts()
        else:
            print("Goodbye")


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


    def sort_selection(self):
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
            return True


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
