
#STEP 1 REQUESTING AN AUTHORIZATION CODE
import requests
import os
import secrets
import hashlib
import base64

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

etsy_client_id = os.getenv('etsy_client_id')
etsy_redirect_uri = os.getenv('etsy_redirect_uri')  #this has to be configured in etsy api dev console

etsy_state = "32165478" #put whatever you want here

code_verifier = secrets.token_urlsafe(50)
#print("Code Verifier For Step 1:", code_verifier)
# Hash the code verifier using SHA-256
code_challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()

# Base64 encode the hashed code challenge
code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).rstrip(b'=').decode()

etsy_code_challenge = code_challenge  #this is the code verifier and configurable. 
etsy_code_challenge_method = "S256" #this is the code verifier and configurable
scope = "shops_r shops_w transactions_r transactions_w listings_r listings_w"

url = "https://www.etsy.com/oauth/connect"

params = {
    "response_type": "code",
    "redirect_uri": etsy_redirect_uri,
    "scope": scope,
    "client_id": etsy_client_id,
    "state": etsy_state,
    "code_challenge": etsy_code_challenge,
    "code_challenge_method": etsy_code_challenge_method
}

response = requests.get(url, params=params)

print(response.url) # this will print the full URL with the parameters encoded
print()
print("Code Challenge For Step 2:", code_verifier)
print()
'''
THIS GAVE THE OUTPUT URL.  CLICK ON IT TO AUTHENTICATE AND GET THE CODE

THIS IS THE REDIRECT URL AND CONTAINS THE CODE AND STATE

'''


'''
scopes
Name	Description
address_r	Read a member's shipping addresses.
address_w	Update and delete a member's shipping address.
billing_r	Read a member's Etsy bill charges and payments.
cart_r	Read the contents of a member’s cart.
cart_w	Add and remove listings from a member's cart.
email_r	Read a member's email address
favorites_r	View a member's favorite listings and users.
favorites_w	Add to and remove from a member's favorite listings and users.
feedback_r	View all details of a member's feedback (including purchase history.)
listings_d	Delete a member's listings.
listings_r	Read a member's inactive and expired (i.e., non-public) listings.
listings_w	Create and edit a member's listings.
profile_r	Read a member's private profile information.
profile_w	Update a member's private profile information.
recommend_r	View a member's recommended listings.
recommend_w	Remove a member's recommended listings.
shops_r	See a member's shop description, messages and sections, even if not (yet) public.
shops_w	Update a member's shop description, messages and sections.
transactions_r	Read a member's purchase and sales data. This applies to buyers as well as sellers.
transactions_w	Update a member's sales data.

'''