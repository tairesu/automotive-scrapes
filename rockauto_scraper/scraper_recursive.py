import requests
from bs4 import BeautifulSoup


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


models = []
trims = []
categories  = []
# Return appropriate URL based on parameters
def handle_url(make, year, model=None, trim=None, category=None, part=None):
    if not model:
        url = f'https://www.rockauto.com/en/catalog/{make},{year}'
    elif not trim:
        url = f'https://www.rockauto.com{model["slug"]}'
    elif not category:
        url = f'https://www.rockauto.com{trim["slug"]}'
    elif category:
        url = f'https://www.rockauto.com{category["slug"]}'
    elif part:
        url = f'https://www.rockauto.com{part["slug"]}'
    return url


def selection(openLinksList) :
    for (i,anchor) in enumerate(openLinksList):
        print(i,anchor['name'])

    selection = int(input("Make a selection"))    
    return openLinksList[selection]

# Call next recursive case based on parameters
def handle_next_recursion(openLinksList, make, year, model=None, trim=None, category=None, part=None):
    if not model:
        # Go deeper with model
        return get_rockauto_data(make, year, model=selection(openLinksList))
    elif not trim:
        print(f'\n\nall trims: \n {openLinksList} \n')
        # Go deeper with trim
        return get_rockauto_data(make, year, model, trim=selection(openLinksList))
    elif not category:
        print(f'\n\nall categories: \n {openLinksList} \n')
        categories = openLinksList
        # Go deeper with category
        return get_rockauto_data(make, year, model, trim, selection(openLinksList))
    elif not part:
        print(f'\n\nall parts: \n {openLinksList} \n')
        categories = openLinksList
        # Go deeper with category
        return get_rockauto_data(make, year, model, trim, selection(openLinksList))

#remove handle next recursion
#create is_parts_present()
#run in main

def get_rockauto_data(make, year, model=None, trim=None, category=None, part=None):
    # Build URL based on state
    url = handle_url(make,year,model,trim,category,part )

    print(f'FETCHING: {url}\n')
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')

    # BASE CASE: table with parts is loaded
    if soup.find('tbody', class_='listing-inner'):
        partsTbodyData = soup.find('tbody', class_='listing-inner')
        print(f"💥 Found {len(partsTbodyData)} Parts")
        return 

    # RECURSIVE CASES
    expandedIcons = soup.find_all('td', class_='nexpandedicon')
    activeTd = expandedIcons[-1]
    activeListDiv = activeTd.find_parent('div', class_='ranavnode')
    activeListAnchors = activeListDiv.find_all('a', class_=["navlabellink","nvoffset","nnormal"])[1:]
    openLinksList = [{'name': a.text.strip(), 'slug': a['href']} for a in activeListAnchors]

    handle_next_recursion(openLinksList, make, year, model, trim, category, part)
    
    
print(get_rockauto_data('honda','2004'))