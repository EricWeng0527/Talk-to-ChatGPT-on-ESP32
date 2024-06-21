import requests


server_url = 'http://127.0.0.1:8000/whisper'
response = requests.post(server_url)
print(response.text)
