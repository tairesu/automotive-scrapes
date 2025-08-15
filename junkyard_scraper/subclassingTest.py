import re
#The premise of this next is move to make adding other junkyards easily via configuring certain variables.


#Both my LKQ and JUP .py files have similar attributes and methods in their classes
#Why not subclass them for testing purposes


#Search()
class Search(): 
	def __init__(self, search_str):
		self.search_str = search_str
		self.results = []
		self.yard_info = {}
		self.base_url = ""
		self.headers = {
			"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		}

	def show_url(self):
		print('Showing base_url:', self.base_url)

	def get_data(self):
		output_dict = self.yard_info
		output_dict['summary'] = f'{len(self.results)} Vehicle(s) Found'
		#output_dict['results'] = self.get_results()
		return output_dict

	def handle_filters(self):
		#Parses the given filters into a comma separated array
		filters_list = self.parse_filters(self.search_str)
		#Loop through that array..
		for filter in filters_list:
			#capture the year/year range conditionals
			conditionals, cleaned_filter = self.parse_filter_conditionals(filter.strip())
			print('conditionals, cleaned_filter: ', conditionals, ',', cleaned_filter)
			#... grab matching vehicles from online inventory that matches the filter, and satisfies the conditional 
			#self.fetch_inventory(filter=cleaned_filter, conditionals=conditionals)


	def parse_filters(self, filters):
		return filters.split(',')

	def parse_filter_conditionals(self, filter):
		conditionals = {}
		semantics = filter.strip().split(' ')
		cleaned_filter = filter.strip()
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
		text = patternmake
		return True if re.findall(r"^(\d{2}-\d{2}\s)|^(\d{4}-\d{4}\s)", text) else False

	def parse_car_year_range(self, pattern):
		text = pattern.replace('–', '-').replace('—', '-')
		range_str = re.findall(r"^\d{2}-\d{2}|^\d{4}-\d{4}", text.strip())[0]
		min_year = range_str.split('-')[0]
		max_year = range_str.split('-')[1]
		min_year = "20" + min_year if len(min_year) == 2 else min_year
		max_year = "20" + max_year if len(max_year) == 2 else max_year
		return (min_year, max_year)

class LKQ(Search):
	def __init__(self,search_str):
		super().__init__(search_str)
		self.base_url = "https://www.lkqpickyourpart.com/DesktopModules/pyp_vehicleInventory/getVehicleInventory.aspx"
		self.headers = {
		"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		"Accept": "*/*",
		"Referer": "https://www.lkqpickyourpart.com/inventory/blue-island-1582/",
		"X-Requested-With": "XMLHttpRequest",
		"Accept-Encoding": "gzip, deflate, br",
		"Accept-Language": "en-US,en;q=0.9"
		}

class JUP(Search):
	def __init__(self,search_str):
		super().__init__(search_str)
		self.yard_info = {'name': 'Joliet U Pull it'}
		self.set_url()

	def set_url(self, make='', model=''):
		self.base_url = f"https://www.jolietupullit.com/inventory/?make={make}&model={model}"


lkq = LKQ('2012-2022 honda, chevrolet tahoe')
jup = JUP('2012-2022 honda, chevrolet tahoe')
print(lkq.handle_filters())
print('\n',jup.handle_filters())
	# def handle_search_str(self, search_str):
    #     #Parses the given search_str into a comma separated array
    #     search_str_list = self.parse_search_str(search_str)
    #     #Loop through that array..
    #     for search_str in search_str_list:
    #         #capture the year/year range conditionals
    #         conditionals, cleaned_search_str = self.parse_search_str_conditionals(search_str.strip())
    #         #... grab matching vehicles from online inventory that matches the search_str, and satisfies the conditional 
    #         self.fetch_inventory(search_str=cleaned_search_str, conditionals=conditionals)

