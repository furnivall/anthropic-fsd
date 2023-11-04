import sys
import requests
from utils import process_data
from api import get_data

response = requests.get('https://example.com/data')
data = response.json()

processed_data = process_data(data)
api_data = get_data()

combined_data = processed_data + api_data
print(combined_data)