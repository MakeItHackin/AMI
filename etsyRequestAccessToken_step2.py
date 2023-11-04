#STEP 2  REQUEST ACCESS TOKEN


import requests
import os
import json
import time

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

etsy_client_id = os.getenv('etsy_client_id')
etsy_redirect_uri = os.getenv('etsy_redirect_uri')  #this has to be configured in etsy api dev console

#paste your code from step 1 here
code_from_step1_result = input("Enter the code from URL step 1: ")

code_verifier = input("Enter the code from CODE VERIFIER step 1: ")

url = "https://api.etsy.com/v3/public/oauth/token"

data = {
    "grant_type": "authorization_code",
    "client_id": etsy_client_id,
    "redirect_uri": etsy_redirect_uri,
    "code": code_from_step1_result,
    "code_verifier": code_verifier
}

response = requests.post(url, data=data)

json_response = response.json()

print(json_response) # this will print the JSON response from the API call

etsyAccessToken = json_response['access_token']
etsyRefreshToken = json_response['refresh_token']

etsy_token_JSON = {
    "etsy_access_token": etsyAccessToken,
    "etsy_refresh_token": etsyRefreshToken,
    "date": time.strftime('%Y-%m-%d %H:%M:%S')
}

with open('etsyTokens.json', 'w') as outfile:
    json.dump(etsy_token_JSON, outfile, indent=4)
    
