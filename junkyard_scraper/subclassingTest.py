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

	def handle_search_str(self, search_str):
        #Parses the given search_str into a comma separated array
        search_str_list = self.parse_search_str(search_str)
        #Loop through that array..
        for search_str in search_str_list:
            #capture the year/year range conditionals
            conditionals, cleaned_search_str = self.parse_search_str_conditionals(search_str.strip())
            #... grab matching vehicles from online inventory that matches the search_str, and satisfies the conditional 
            self.fetch_inventory(search_str=cleaned_search_str, conditionals=conditionals)

