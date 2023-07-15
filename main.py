import requests
import pandas  as pd


url = "https://api.collectapi.com/gasPrice/allUsaPrice"
apiKey = 'apikey 3AfMH30uMQazfbAMRpmBKe:3Ogh20ZJ3Pq0h6ezPKvhMZ'


"""
Get the price og gas by making a GET request to the specified URL with the given headers.
    
Returns:
    The JSON response containing the price information.
"""
def get_price():
    headers = {
        'Authorization': apiKey,
        'Content-Type': 'application/json'
        }
    response = requests.request("GET", url, headers=headers)
    return response.json()

data = get_price()
#print(data['result'])
df = pd.json_normalize(data['result'])
print(df.head())
print(list(df.columns))


