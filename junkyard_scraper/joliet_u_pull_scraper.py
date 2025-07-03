from bs4 import BeautifulSoup
import requests


results = ''
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}
      
def fetch_junkyard_data(make='', model='', ignore_headers=False):
    junkyard_url = f'https://www.jolietupullit.com/inventory/?make={make}&model={model}'
    junkyard_html = requests.get(junkyard_url, headers=headers).text
    soup = BeautifulSoup(junkyard_html, 'html.parser')
    #Grabs Joliet U Pull it's inventory as HTML table
    results_table = soup.find(id="cars-table")
    
    # If table has no data
    if not results_table.find(['td']):
        print(f"Could not find {make} {model}'s")
        return ''
    else:
        raw_data = results_table.find_all('tr')
        if ignore_headers:
            raw_data = raw_data[1:]
        return parse_junkyard_data(raw_data)


def parse_junkyard_data(raw_junkyard_data, mode='csv', ignore_headers=False):
    
    
    if mode == 'csv':
        junkyard_data = ''
        
        for i, row in enumerate(raw_junkyard_data):
            cells = row.find_all(['th', 'td'])
            cols = [cell.get_text(strip=True) for cell in cells]
            
            # Add header row
            if i == 0 and row.find('th'):
                junkyard_data = ','.join(cols) + '\n'
            # Add record row
            elif len(cols) >= 6 :
                junkyard_data += f"{cols[0]},{cols[1]},{cols[2]},{cols[3]},{cols[4]},{cols[5]}\n"
        return junkyard_data
    

def valid_query(query):
    car_queries = query.strip().split(',')
    for request in car_queries:
        if (len(request.strip().split(' ')) > 2):
            return False

    return True

# Turns a query str to a list of make/model dictionaries
def parse_queries(query):
    queries = []
    if(not valid_query(query)):
        return False
    
    for car in query.strip().split(','):
        if (len(car.strip().split(' ')) == 1):
            queries.append({
                'make':car.strip().split(' ')[0].upper(),
                'model' : '',
            })
        elif(len(car.strip().split(' ')) == 2):
            queries.append({
                'make':car.strip().split(' ')[0].upper(),
                'model':car.strip().split(' ')[1].upper()
            })
    return queries

def handle_queries(query):
    results = ''
    queries = parse_queries(query)
    for i,make_model in enumerate(queries):
        # Ignore headers if count > 1
        if(i > 0):
            results += fetch_junkyard_data(make_model['make'],make_model['model'], True)
        else:
            results += fetch_junkyard_data(make_model['make'],make_model['model'], False)

    print(results)
     
if __name__ == "__main__":
    halt_input = False
    while (not halt_input) :
        query = input('Whatchu need?')
        if (query == 'exit') :
            halt_input = True
        else:
           handle_queries(query)
