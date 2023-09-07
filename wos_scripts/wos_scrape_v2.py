import requests

api_key = "d8563637cb760fd52eb2d1dde0293b6e24752e74"
endpoint_url = "https://api.clarivate.com/apis/wos-journals/v1"

headers = {
    "Authorization": f"Bearer {api_key}"  # Use "Bearer" prefix if required
}

params = {
    "query": "AU=(Smith) AND PY=2023",
    "pageSize": 3
}

response = requests.get(endpoint_url, params=params, headers=headers)

# Check for a successful response (HTTP status code 200)
if response.status_code == 200:
    data = response.json()
    # Process the data as needed
else:
    print(f"Error: {response.status_code} - {response.text}")

print('done')