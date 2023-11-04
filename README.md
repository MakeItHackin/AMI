# Automated Marketplace Interface  
"Your One-Stop Shop"  

## Requirements  
Check out the requirements file for what to install  

## Environment file  
take the env_example.txt file, edit, and save as '.env' (no file name)  

## Streamlit  
This project uses Streamlit to create the web app.  To run, navigate to your folder path and execute: streamlit run AutomatedMarketplaceInterface.py  

## Tindie  
This project can be used with Tindie Marketplace.  
Tindie info will be updated here.  

## Etsy  
This project can be used with Etsy Marketplace.  
Etsy info will be updated here.  
Etsy uses oAuth2.0 and Proof for Key Exhange for API authentication.  Use the etsyRequestAuthorizationCode_step1.py and etsyRequestAccessToken_step2.py to set up your Etsy Access Tokens.  
More information on authenticating with the Etsy API can be found here:  https://developers.etsy.com/documentation/  

## Lectronz  
This project can be used with Lectronz Marketplace.  
Lectronz info will be updated here.  

## Shpify  
This project can be used with Shopify Marketplace.  
Shopify info will be updated here.  


## Known Issues/Bugs  
Not everything in the GUI is technically usable.  Some of the features are placeholders for work in progress.  If you click a button or make an action and nothing happens, look in the code to see if the action is just an empty function.  
Orders:  Tab should be fully working.  
Code Uploader: Tabe should be fully working.  
Mass Order Fulfillment:  Not functional.  But shows a proof of concept.  Will be updated soon.  
Shipping Labels:  The Shipping Label top half of the page is functional.  The Manifests is a work in progress.  
Packaging:  Not functional.  But shows a proof of concept.  Will be updated soon.  
Inventory:  Partially working.  Inventory updates only working with Lectronz right now.  Will be updated for other platforms.  
Communication:  Paritally working.  Only the send email button hasn't been enabled, but will be updated soon.  Generate AI email works.  
Promotion:  Not functional.  But shows a proof of concept.  Will be updated soon.  
Reverse Engineering:  Partially working.  The cURL command input field is a little sensitive to format.  cURL exports from Google Chrome SHOULD work.  If you see more than two choices when copying cURL from Chrome, choose "as bash".  
Promotion:  partially Working.  The only two functions that are enabled are the "Order Data Source" which is default to simulated data (which you can change) and the button to reset the "combined_orders_in_json" file.  Will be updated soon.  
Notes:  Works!  It's a simple notepad app.  Make sure to save since it doesn't auto-save



