import requests, json;
url = 'https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/honda?format=json';
r = requests.get(url)
print(r.text)
			