from bs4 import BeautifulSoup
import requests
import io
import pandas as pd
import re

def is_year_present(pattern):
    # print('(is_year_present) patterm:', pattern)
    text = pattern.replace('–', '-').replace('—', '-')
    return True if re.findall(r"^\d{2}\s|^\d{4}\s", text) else False

def is_year_range_present(pattern):
    text = pattern.replace('–', '-').replace('—', '-')
    return True if re.findall(r"^(\d{2}-\d{2}\s)|^(\d{4}-\d{4}\s)", text) else False

def parse_car_year(pattern):
    text = pattern.replace('–', '-').replace('—', '-')
    desired_car_year = re.findall(r"^\d{2}\s|^\d{4}\s", text)[0].strip()
    # print(f'parse_car_year({pattern}) desired_car_year:', len(desired_car_year))
    desired_car_year = desired_car_year if len(desired_car_year) == 4 else f"20{desired_car_year}"
    return desired_car_year

def parse_car_year_range(pattern):
    text = pattern.replace('–', '-').replace('—', '-')
    range_str = re.findall(r"^\d{2}-\d{2}|^\d{4}-\d{4}", text.strip())[0]
    min_year = range_str.split('-')[0]
    max_year = range_str.split('-')[1]

    return (min_year,max_year)

class JunkyardScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        self.results = ""
        self.cached_results = []
        self.row_headers = []

    def add_to_history(self, search):
        with open(".search_history.txt", "a") as search_history_file:
            search_history_file.write(f'\n{search}')


    def get_search_history(self):
        search_history = []
        search_history_file = open(".search_history.txt", "r")
        for line in search_history_file:
            search_history.append(line.strip().replace("\n",""))
        search_history_file.close()
        print('(get_search_history) search_history: ', search_history)
        return search_history

    def valid_query(self, query):
        
        car_queries = query.strip().split(',')
        for request in car_queries:
            if len(request.strip().split(' ')) > 4:
                return False
        return True

# Chevrolet Tahoe, GMC Yukon, Cadillac Escalade, Chevrolet Silverado, GMC Sierra, Chevrolet Avalanche, Chevrolet Suburban, GMC Yukon XL, Chevrolet TrailBlazer, GMC Envoy, Buick Rainier, Saab 9-7X, Isuzu Ascender, Hummer H3, Chevrolet Colorado, GMC Canyon

    def set_results(self, results):
        self.results = results


    def cache_result(self, result):
        self.cached_results.append(result)


    # maps given string to dictionary of cars            
    def parse_queries(self, query):
        if not self.valid_query(query):
            return False
        
        queries = []
        #Loop through each section of starting query
        for car_search in query.strip().split(','):   
            car_search_dict = self.format_car_search(car_search)         
            #Append dictionary containing make, model, year
            queries.append(car_search_dict)
        return queries


    def fetch_results(self, query):
        parsed = self.parse_queries(query)
        if not parsed:
            print("[!] Invalid query format.")
            return ''

        self.add_to_history(query)
        for i, car in enumerate(parsed):
            self.results += self.fetch_junkyard_data(
                car['make'], car['model'], car['year'], car['min_year'], car['max_year'], ignore_headers=(i > 0)
            )
        self.set_results(self.results)
        self.cache_result(self.results)
        return self.results


    #Gets car model from list of search components 
    def get_car_model(self, car_search_components):
        model = ''
        #If the search contains 1 dividing space 
        if len(car_search_components) == 2:
            #Set model to second item in search components
            model = car_search_components[1].upper()
        #If the search contains 2 diving spaces
        elif len(car_search_components) == 3:
            #Set model to the first and second items in search components
            model = car_search_components[1].upper() + '+' + car_search_components[2].upper()

        return model


    #Format raw car_search str into dictionary:
    #"2004 Honda Civic" => {year:"2004", make:"Honda"...})
    #"2004-2007 Honda Civic" => {min_year:2004, max}
    def format_car_search(self, car_search_str):
        year = ''
        min_year = ''
        max_year = ''
        car_search_query = car_search_str.strip()
        search_components = car_search_query.split(' ') #Breaks starting query string into list of components
        # print(f'[format_car_search] is_year_present:', is_year_present(car_search_query))
        # print(f'[format_car_search] is_year_range_present:', is_year_range_present(car_search_query))
        if is_year_present(car_search_query):
            #Set the year 
            # print(f'[format_car_search] Just a year in {car_search_query} query')
            year = parse_car_year(car_search_query)
            make = search_components[1].upper()
            search_components.pop(0)

        elif is_year_range_present(car_search_query):
            # print(f'[format_car_search] Year range present in {car_search_query} query')
            min_year, max_year= parse_car_year_range(car_search_query)
            make = search_components[1].upper()
            search_components.pop(0)

        else:
            #Set the make to first item in search components
            make = search_components[0].upper()
        #Gets the model based on search componentslength 
        model = self.get_car_model(search_components)
        # print('[format_car_search] output dictionary: ', {'make': make, 'model': model, 'year': year, 'min_year': min_year, 'max_year': max_year})
        return {'make': make, 'model': model, 'year': year, 'min_year': min_year, 'max_year': max_year}

    def filter_vehicle(self, cols, year, min_year,max_year):
        result = ''
        vehicle_is_year = (year != '' and cols[0] == year)
        vehicle_in_year_range = (min_year!='' and max_year!='' and int(cols[0]) in range(int(min_year), int(max_year)+1))
        ignore_year_and_range = (year =='' and min_year =='' and max_year =='')
        #print(f'\n[parse_site_table_rows] vehicle:{cols[0] + " " + cols[1] + cols[2]}\nvehicle_has_year:{vehicle_is_year}\nvehicle_in_year_range:{vehicle_in_year_range}\nignore_year_and_range:{ignore_year_and_range}\n')
        #if year is found within the first column  Or year is not passed 
        if ignore_year_and_range or vehicle_is_year or vehicle_in_year_range:
            #Format table header text list as csv 
            result += ','.join(cols[:6]) + '\n'
        else:
            result += ''


        return result

    #cleans vehicle data from given HTML table rows 
    def parse_site_table_rows(self, table_rows, year='', min_year='', max_year ='', mode='csv'):
        if mode != 'csv':
            raise ValueError("Only CSV mode is currently supported.")
        cleaned_data = ''
        for i, table_row in enumerate(table_rows):
            #Grab all th and td elements from a table row 
            cells = table_row.find_all(['th', 'td'])
            #Creates a list of inner text from the table row elements)
            cols = [cell.get_text(strip=True) for cell in cells]
            #If first time looping, and a table header element exists 
            if i == 0 and table_row.find('th'):
                #set row headers to the table header text list 
                self.row_headers = cols
                #format table header text list to CSV 
                cleaned_data = ','.join(cols) + '\n'
            elif len(cols) >= 6:
                cleaned_data += self.filter_vehicle(cols, year, min_year, max_year)
                
        return cleaned_data

    
    def fetch_junkyard_data(self, make='', model='',year='',min_year='',max_year='', ignore_headers=False):
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
        
        return self.parse_site_table_rows(rows,year,min_year,max_year)

    
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

    
    def ask_what_next(self):
        callbacks = {
            'Sort Cars': self.handle_sort_by,
            'Filter Cars': self.handle_filter,
            'View History': self.handle_search_history,
            'New Search': self.handle_search,

        }
        #print(f'[ask_what_next] len cacched_results: {len(self.cached_results)}')
        print("Actions:")
        if len(self.cached_results) > 1:
            callbacks['Go Back'] = self.handle_go_back

        opts = list(callbacks.keys())
        #Display fiven options 
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

    def search_history_selection(self):
        print("\n Searching through history")
        opts = self.get_search_history()
        self.display_options(opts,numbers_on=True)
        choice = input(f"Which search to execute? [0-{len(opts)-1}]: ")
        if choice.lower() == 'exit':
            return False
        if choice.isdigit() and int(choice) in range(len(opts)):
            self.results = ''
            self.fetch_results(opts[int(choice)])
            return True


    def handle_search(self):
        self.results = ''
        if(self.choose_opts(self.car_selection)):
            self.choose_opts(self.ask_what_next)
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
        self.choose_opts(self.ask_what_next)


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
            if(self.choose_opts(self.sort_selection)):
                self.choose_opts(self.ask_what_next)
        else:
            print("[!] There aren't any results to sort. \n")

    def handle_search_history(self):
         if(self.results):
            try:
                if(self.choose_opts(self.search_history_selection)):
                    self.choose_opts(self.ask_what_next)
            except Exception as e:
                print('Try Again\n')
                self.handle_search()   

    
    def handle_filter(self, retries=3):
        if(self.results):
            try:
                if(self.choose_opts(self.filter_selection)):
                    self.choose_opts(self.ask_what_next)
            except Exception as e:
                print('Try Again\n')
                self.handle_filter(retries=retries-1)         

    
    def choose_opts(self, func):
        stop = func()
        #print(f'[choose_opts] func:{func} , stop is :{stop}')
        while not stop:
            pass

        return True

# Run it
if __name__ == "__main__":
    scraper = JunkyardScraper()
    scraper.handle_search()
