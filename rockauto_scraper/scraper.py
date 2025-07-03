import requests
from bs4 import BeautifulSoup

# Return appropriate Rockauto URL based on parameters
def get_rockauto_url(make, year, model=None, trim=None, category=None, part=None):
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


def make_decision(opts) :
    for (i,anchor) in enumerate(opts):
        print(i,anchor['name'])

    choice = int(input("Make a selection"))    
    return opts[choice]

# Returns Code from a rockauto url
def get_page_html(url):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')
    return soup

# Checks rockauto url for parts table
def is_parts_present(url):
    # Grabs page HTML
    soup = get_page_html(url)
    # Rockauto Parts Tables
    partsTables = soup.find('tbody', class_='listing-inner')
    # Table with parts is loaded
    if partsTables:
        print(f"💥 Found {len(partsTables)} Parts")
        return True 
    return False
    
# Return the list of expanded rockauto items    
def grab_rockauto_links(url):
    # RECURSIVE CASES
    soup = get_page_html(url)
    expandedIcons = soup.find_all('td', class_='nexpandedicon')
    activeTd = expandedIcons[-1]
    activeListDiv = activeTd.find_parent('div', class_='ranavnode')
    activeListAnchors = activeListDiv.find_all('a', class_=["navlabellink","nvoffset","nnormal"])[1:]
    openLinksList = [{'name': a.text.strip(), 'slug': a['href']} for a in activeListAnchors]
    return openLinksList


def get_url_postselection(choice,make,year,model=None,trim=None,category=None,part=None):
    if not model:
        url = get_rockauto_url(make,year,model=choice)
    elif not trim:
        url = get_rockauto_url(make,year,model,trim=choice)
    elif not category:
        url = get_rockauto_url(make,year,model,trim,category=choice)
    elif not part:
        url = get_rockauto_url(make,year,model,trim,category,part=choice)

    return url


def get_rockauto_data(make, year, model=None, trim=None, category=None, part=None):
    # Build URL based on state
    url = get_rockauto_url(make,year,model,trim,category,part)
    return grab_rockauto_links(url)

    
if __name__ == '__main__':
    make = input('What make?: ')
    year = input('What year?: ')
    model = {}
    trim = {}
    category = {}
    part = {}

    url = get_rockauto_url(make,year)
    while (not is_parts_present(url)):
        rockautoListItems = grab_rockauto_links(url)
        choice = make_decision(rockautoListItems)
        print("You selected: \n", choice)
        
        #Get new Url from ListItem selection
        url = get_url_postselection(choice,make,year,model,trim,category,part)
