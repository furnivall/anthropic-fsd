import requests

def get_data():
response = requests.get('https://example.com/api-data')
return response.json()