import requests

url = requests.get('https://www.google.com')
print(url.content)
