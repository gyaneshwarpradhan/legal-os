import requests, json, sys
url = 'http://127.0.0.1:8000/api/v1/auth/login'
payload = {'email': 'admin@legalos.local', 'password': 'admin123'}
resp = requests.post(url, json=payload)
print('Status code:', resp.status_code)
print('Response:', resp.text)
