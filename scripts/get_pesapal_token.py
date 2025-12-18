import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('PESAPAL_TOKEN_URL')
key = os.getenv('PESAPAL_CONSUMER_KEY')
secret = os.getenv('PESAPAL_CONSUMER_SECRET')
print('Token URL:', url)
print('Consumer Key present:', bool(key))
print('Consumer Secret present:', bool(secret))
try:
    resp = requests.post(url, json={"consumer_key": key, "consumer_secret": secret}, timeout=15)
    print('Status:', resp.status_code)
    try:
        print('JSON:', resp.json())
    except Exception:
        print('Text:', resp.text)
except Exception as e:
    print('Error:', repr(e))
