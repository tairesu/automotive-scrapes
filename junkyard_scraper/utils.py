class YardSearch():
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