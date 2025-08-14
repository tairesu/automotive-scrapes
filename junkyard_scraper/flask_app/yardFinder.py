from jup import JupSearch 
from lkq import LKQSearch

def handleSearch(search_str, output=False):
	jup = JupSearch(search_str)
	lkq = LKQSearch(search_str)
	if output:
		jup.display_data()
		lkq.display_data()
		return ''



if __name__ == '__main__':
	stop = False
	while(stop != True):
		unfiltered_search = input('Enter year, make, model')
		if unfiltered_search in ['exit','stop']:
			stop = True
		else:
			handleSearch(unfiltered_search, output=True)