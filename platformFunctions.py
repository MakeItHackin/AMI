import json
import requests

#import sys
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.parse
import time
from datetime import datetime, timedelta

from seleniumwire import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire.utils import decode

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

shopify_access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
etsy_client_id = os.getenv('etsy_client_id')
MY_ADDRESS = os.getenv('MY_ADDRESS')
PASSWORD = os.getenv('PASSWORD')
myEmail = os.getenv('myEmail')

etsy_shop_id = os.getenv('etsy_shop_id')
email_server = os.getenv('email_server')
email_server_port = os.getenv('email_server_port')
tindie_username = os.getenv('tindie_username')
tindie_password = os.getenv('tindie_password')

lectronz_bearer_token = os.getenv('lectronz_bearer_token')

###############################################################################

windowsOSBoolean = True


script_path = os.path.abspath(__file__)
# Get the directory containing the script
codePath = os.path.dirname(script_path)

if ('/home/pi/' in codePath):
    windowsOSBoolean = False
    #print(codePath, "this is the pi")
else:
    #print(codePath, "this is windows")
    pass


###############################################################################
   
###############################################################################
    
def getNewEtsyAccessToken():
    
    with open('etsyTokens.json') as file:
        etsy_token_file = json.load(file)
    
    etsy_access_token = etsy_token_file['etsy_access_token']
    etsy_refresh_token = etsy_token_file['etsy_refresh_token']
    
    url = "https://api.etsy.com/v3/public/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": etsy_client_id,
        "refresh_token": etsy_refresh_token
    }

    response = requests.post(url, data=data)
    etsyAccessToken = response.json()['access_token']
    etsyRefreshToken = response.json()['refresh_token']

    etsy_token_JSON = {
        "etsy_access_token": etsyAccessToken,
        "etsy_refresh_token": etsyRefreshToken,
        "date": time.strftime('%Y-%m-%d %H:%M:%S')
    }

    with open('etsyTokens.json', 'w') as outfile:
        json.dump(etsy_token_JSON, outfile, indent=4)

    return(etsyAccessToken)
    
###############################################################################

def sendEmailToCustomer(orderDetails, shipDateForCustomer):

    print('########################################################')
    
    emailSent = False
    testMode = False
    

    buyerEmail = orderDetails['buyer_email']
    buyerName = orderDetails['buyer_name']
    isBuyerRepeat = orderDetails['buyer_is_repeat']
    orderState = orderDetails['order_state']
    buyerNotes = orderDetails['order_notes']
    isGift = orderDetails['order_is_gift']
    giftMessage = orderDetails['order_gift_message']
    hasUnreadMessage = orderDetails['order_has_unread_message']
    paymentTotal = orderDetails['order_payment_total']
    taxTotal = orderDetails['order_tax_total']
    shippingTotal = orderDetails['order_shipping_total']
    itemsTotal = orderDetails['order_items_total']
    shippingMethod = orderDetails['order_shipping_method']
    productsOrdered = orderDetails['products']
    shipByDate = orderDetails['ship_by_date']
    platform = orderDetails['platform']
    orderID = orderDetails['order_id']
    orderDate = orderDetails['order_date']
    canadianTax = orderDetails['canadian_tax']

    is_awaiting_instructions = orderDetails['personalized_ordered_with_no_instructions']
    

    print('Sending Email...')


    productListString = ''


    for product in productsOrdered:
        productName = product['product_name']
        productQuantity = product['product_quantity']
        productType = product['product_type']
        personalization = product['personalization']
        personalization = cleanUpTextForRecieptPrinter(personalization)
        if (productType == ''):
            productListString =  productName + '\nQuantity: ' + str(productQuantity) + '\n\n' + productListString
        else:
            productListString =  productName + '\n' + productType + '\nQuantity: ' + str(productQuantity) + '\n\n' + productListString

    s = smtplib.SMTP(email_server,email_server_port)
    s.starttls() #only for non SSL
    s.login(MY_ADDRESS,PASSWORD)

    if (testMode == True):
        buyerEmail = myEmail
    msg = MIMEMultipart()       # create a message
    msg['To']=buyerEmail #myEmail
    msg['From']=MY_ADDRESS
    

    platformForEmail = platform.capitalize()
    
    if (platformForEmail == 'Mih'):
        platformForEmail = 'Shopify'

    if (is_awaiting_instructions == False):
        msg['Subject']= 'Your ' + platformForEmail + ' Order #' + str(orderID) + ' will be shipped ' + shipDateForCustomer + '  :)'
        message = ("Hello and thank you for your order from the v store on " + platformForEmail + "!\n\n"
            + "Your order will be shipped out soon and you will receive a notification from " + platformForEmail + " with the tracking number once it has been shipped.\n"
            + "If you have any questions, please feel free to email or send a message on " + platformForEmail + ".\n"
            + "Thanks again and have a wonderful day!\n\n"
            + "- [name]/[store_name] \n\n"
            + "ORDER DETAILS:\n"
            + "Order ID: " + str(orderID) + "\n"
            + "Order Date: " + str(orderDate) + "\n"
            + "Buyer: " + str(buyerName) + "\n"
            + "Shipping Method: " + str(shippingMethod) + "\n"
            + "Payment Total: " + str(paymentTotal) + "\n"
            + "Buyer Notes: " + str(buyerNotes) + "\n\n"
            + "Products Ordered:\n" + productListString
            )
        
    elif (is_awaiting_instructions == True):
        msg['Subject']= 'Personalization Required for Your ' + platformForEmail + ' Order #' + str(orderID)
        message = ("Hello and thank you for your order from the [store_name] store on " + platformForEmail + "!\n\n"
            + "I am reaching out to you to see how you would like to personalize your order. \n"
            + "Please reply to this email with your personalization instructions.  If you have any questions, please feel free to email or send a message on " + platformForEmail + ".\n\n"
            + "Thanks again and have a wonderful day!\n"
            + "- [name]/[store_name] "
            )

    
    msg.attach(MIMEText(message, 'plain'))
    s.send_message(msg)
    del msg
    s.quit()
    print("Email Sent to", buyerEmail, 'Order', str(orderID))
    emailSent = True
    print('########################################################')
    return(emailSent)


###############################################################################

def cleanUpTextForRecieptPrinter(text):
    
    updated_string = text.replace('“', '"')
    updated_string = updated_string.replace('”', '"')
    updated_string = updated_string.replace('’', "'")
    updated_string = updated_string.replace('‘', "'")
    updated_string = updated_string.replace('–', "-")
    updated_string = updated_string.replace('—', "-")
    updated_string = updated_string.replace('…', "...")
    updated_string = updated_string.replace('™', "(TM)")
    updated_string = updated_string.replace('®', "(R)")
    updated_string = updated_string.replace('©', "(C)")
    updated_string = updated_string.replace('°', "deg")
    updated_string = updated_string.replace('•', "*")
    updated_string = updated_string.replace('²', "2")
    updated_string = updated_string.replace('³', "3")
    updated_string = updated_string.replace('¼', "1/4")
    updated_string = updated_string.replace('½', "1/2")
    updated_string = updated_string.replace('¾', "3/4")
    updated_string = updated_string.replace('×', "x")
    updated_string = updated_string.replace('÷', "/")
    updated_string = updated_string.replace('≤', "<=")
    updated_string = updated_string.replace('≥', ">=")
    updated_string = updated_string.replace('≠', "!=")
    updated_string = updated_string.replace('≈', "~")
    updated_string = updated_string.replace('±', "+/-")
    updated_string = updated_string.replace('µ', "u")
    updated_string = updated_string.replace('∞', "oo")
    updated_string = updated_string.replace('√', "sqrt")
    updated_string = updated_string.replace('∆', "delta")
    updated_string = updated_string.replace('∑', "sum")
    updated_string = updated_string.replace('∏', "prod")
    updated_string = updated_string.replace('∫', "int")
    updated_string = updated_string.replace('∮', "oint")
    updated_string = updated_string.replace('∴', "therefore")
    updated_string = updated_string.replace('∵', "because")
    updated_string = updated_string.replace('∼', "~")
    updated_string = updated_string.replace('≡', "==")
    updated_string = updated_string.replace('≅', "~")
    updated_string = updated_string.replace('≈', "~")
    updated_string = updated_string.replace('≠', "!=")
    updated_string = updated_string.replace('≡', "==")
    updated_string = updated_string.replace('≤', "<=")
    updated_string = updated_string.replace('≥', ">=")
    updated_string = updated_string.replace('≪', "<<")
    updated_string = updated_string.replace('≫', ">>")
    updated_string = updated_string.replace('⊂', "subset of")
    updated_string = updated_string.replace('⊃', "superset of")
    updated_string = updated_string.replace('⊆', "subset of or equal to")
    updated_string = updated_string.replace('⊇', "superset of or equal to")
    updated_string = updated_string.replace('⊕', "+")
    updated_string = updated_string.replace('⊗', "x")
    updated_string = updated_string.replace('⊥', "perpendicular")
    updated_string = updated_string.replace('⋅', ".")
    updated_string = updated_string.replace('⌈', "[")
    updated_string = updated_string.replace('⌉', "]")
    updated_string = updated_string.replace('⌊', "[")
    updated_string = updated_string.replace('⌋', "]")
    updated_string = updated_string.replace('〈', "<")
    updated_string = updated_string.replace('〉', ">")

    updated_string = updated_string.replace('č', "c")
    updated_string = updated_string.replace('&quot;', "\"")
    updated_string = updated_string.replace('&#39;', "\'")
    updated_string = updated_string.replace('&lt;', "<")
    
    return(updated_string)



###############################################################################


def getShopifyFulfillmentOrder(orderID):
    
    url = f"https://your-store-name.myshopify.com/admin/api/2023-01/orders/{orderID}/fulfillment_orders.json"

    payload={}
    headers = {
    'X-Shopify-Access-Token': shopify_access_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    json_response = response.json()
    pretty_json = json.dumps(json_response, indent=4)
    #print(pretty_json)
    try:
        fulfillmentOrder = json_response['fulfillment_orders'][0]
        fulfillmentOrderID = fulfillmentOrder['id']
        assigned_location_id = fulfillmentOrder['assigned_location_id']
        request_status = fulfillmentOrder['request_status']
        status = fulfillmentOrder['status']
        supported_actions = fulfillmentOrder['supported_actions']
        fulfill_by = fulfillmentOrder['fulfill_by']
        delivery_method = fulfillmentOrder['delivery_method']
        shop_id = fulfillmentOrder['shop_id']
        order_id = fulfillmentOrder['order_id']
    except:
        fulfill_by = ''
    return(fulfill_by)


###############################################################################
###############################################################################


def fulfillShopifyOrder(orderID, locationID, trackingCompany, trackingNumber, trackingURL):

    url = f"https://your-store-name.myshopify.com/admin/api/2022-04/orders/{orderID}/fulfillments.json"

    payload = json.dumps({
        "fulfillment": {
        "notifyCustomer": False,
        "location_id": locationID,
        "tracking_company": trackingCompany,
        "tracking_number": trackingNumber,
        "tracking_url": trackingURL
        }
    })
    headers = {
    'X-Shopify-Access-Token': shopify_access_token,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print('RESPONSE TEXT ---- ', response.text)
    print('RESPONSE STATUS CODE ---- ', response.status_code)
    
    json_response = response.json()
    #print('##################################################################')
    #print(json_response)
    #print('##################################################################')
    if (response.status_code != 200):
        pretty_json = json.dumps(json_response, indent=4)
        print('FULFILL SHOPIFY ORDRER JSON ---- ', pretty_json)
        print('RESPONSE STATUS CODE ---- ', response.status_code)
    #print('FULFILL SHOPIFY ORDRER JSON ---- ', pretty_json)
    fulfillmentJSON = json_response['fulfillment']
    fulfillmentID = fulfillmentJSON['id']
    fulfillmentStatus = fulfillmentJSON['status']
    
    return(fulfillmentID, fulfillmentStatus, response.status_code)

####################################################################################################################################

def fulfillEtsyOrder(orderID, trackingCompany, trackingNumber, dateShipping):

    etsy_access_token = getNewEtsyAccessToken()
    
    trackingCompany = 'usps'
    trackingNumber = str(trackingNumber)
    
    url = f"https://api.etsy.com/v3/application/shops/{etsy_shop_id}/receipts/{orderID}/tracking"

    payload = json.dumps({
        "tracking_code": trackingNumber,
        "note_to_buyer": "Your order is being prepared and will be shipped on " + dateShipping,
        "carrier_name": trackingCompany
    })
    headers = {
    "x-api-key": etsy_client_id,
    "Authorization": 'Bearer ' + etsy_access_token,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    json_response = response.json()

    #print('##################################################################')
    #print(json_response)
    #print('##################################################################')
    pretty_json = json.dumps(json_response, indent=4)
    #fulfillmentJSON = json_response['fulfillment']
    if (response.status_code == 200):
        is_shipped = json_response['is_shipped']
        fulfillmentStatus = json_response['status']
    else:
        print('FULFILL ETSY ORDRER JSON ---- ', pretty_json)
        print('RESPONSE STATUS CODE ---- ', response.status_code)
        is_shipped = False
        fulfillmentStatus = 'error'
    
    return(is_shipped, fulfillmentStatus, response.status_code)


####################################################################################################################################

def urlencode_string(input_string):
    # URL-encode the input string
    encoded_string = urllib.parse.quote(input_string)
    return encoded_string


####################################################################################################################################

def fulfillTindieOrder(orderID, trackingCompany, trackingNumber, dateShipping):
    
    with open('tindieCookie.json') as file:
        tindie_cookie_file = json.load(file)
    
    tindie_csrf_middleware_token = tindie_cookie_file['csrfMiddleWareToken']
    tindie_cookie = tindie_cookie_file['tindieCookie']
    user_agent = tindie_cookie_file['userAgent']
    
    messageToSend = 'Thank you so much for your order!  It is being prepared and will be shipped ' + dateShipping
    
    messageToSend = urlencode_string(messageToSend)
    
    url = "https://www.tindie.com/orders/" + orderID + "/"
    
    payload = 'csrfmiddlewaretoken=' + tindie_csrf_middleware_token + '&message=' + messageToSend + '&tracking_code=' + str(trackingNumber) + '&save=Shipped'
    
    headers = {
      'authority': 'www.tindie.com',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
      'accept-language': 'en-US,en;q=0.9',
      'cache-control': 'max-age=0',
      'content-type': 'application/x-www-form-urlencoded',
      'cookie': tindie_cookie,
      'dnt': '1',
      'origin': 'https://www.tindie.com',
      'referer': 'https://www.tindie.com/orders/' + orderID + '/',
      'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"Windows"',
      'sec-fetch-dest': 'document',
      'sec-fetch-mode': 'navigate',
      'sec-fetch-site': 'same-origin',
      'sec-fetch-user': '?1',
      'upgrade-insecure-requests': '1',
      'user-agent': user_agent
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    print('FULFILL TINDIE----', response.status_code, response.reason)
    
    return(response.status_code)
    
####################################################################################################################################

def updateLectronzProductInventory(product_id_to_update, inventoryLevel):
        
    lectronz_update_product_url = f'https://lectronz.com/api/v1/products/{product_id_to_update}' 

    print('Updating Lectronz Inventory...')

    
    payload={"stock_available": inventoryLevel}
    headers = {
    'Authorization': 'Bearer '+ lectronz_bearer_token
    }       

    response = requests.request("PATCH", lectronz_update_product_url, headers=headers, data=payload)

    if (response.status_code == 200):
        json_response = response.json()
        stock_level = json_response['stock_available']
    else:
        print('FULFILL LECTRONZ ORDRER JSON ---- ', response.text)
        print('RESPONSE STATUS CODE ---- ', response.status_code)
        #is_shipped = False
        stock_level = 'error'
    
    return(stock_level, response.status_code)

####################################################################################################################################

def fulfillLectronzOrder(orderID, trackingNumber):

    trackingNumber = str(trackingNumber)
    
    lectronz_fulfill_url = f"https://lectronz.com/api/v1/orders/{orderID}"    

    payload = json.dumps({
        "tracking_code": trackingNumber,
        "tracking_url": "https://tools.usps.com/go/TrackConfirmAction?tLabels=" + trackingNumber,
        "status": "fulfilled"
        
    })
    headers = {
    "Authorization": 'Bearer ' + lectronz_bearer_token,
    'Content-Type': 'application/json'
    }

    response = requests.request("PATCH", lectronz_fulfill_url, headers=headers, data=payload)

    
    json_response = response.json()

    pretty_json = json.dumps(json_response, indent=4)
    
    if (response.status_code == 200):
        #is_shipped = json_response['is_shipped']
        fulfillmentStatus = json_response['status']
    else:
        print('FULFILL LECTRONZ ORDRER JSON ---- ', pretty_json)
        print('RESPONSE STATUS CODE ---- ', response.status_code)
        #is_shipped = False
        fulfillmentStatus = 'error'
    
    return(fulfillmentStatus, response.status_code)
    

###################################################################################################################################

def getNewTindieCookie():
    print('getting new tindie cookies...')
    loginURL = 'https://www.tindie.com/accounts/login/'
    csrftoken = ''
    sessionid = ''
    tindieCookie = ''
    cookieFound = False
    options = webdriver.ChromeOptions()
    
    options.add_argument('--headless')

    driver = webdriver.Chrome(options=options) 
    driver.get(loginURL)
    
    try:
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='id_auth-password']")))   
    except:
        print('Webdriver Wait Timeout')
        
    
    usernameInput = driver.find_element(by=By.XPATH, value="//*[@id='id_auth-username']")
    passwordInput = driver.find_element(by=By.XPATH, value="//*[@id='id_auth-password']")
    button = driver.find_element(by=By.XPATH, value="//*[@id='submit-id-login']")
    
    element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='submit-id-login']")))
    driver.execute_script("arguments[0].scrollIntoView();", element)
    
    usernameInput.send_keys(tindie_username)
    passwordInput.send_keys(tindie_password)
    
    time.sleep(1)

    button.click()
        
    print('Waiting to load...')
    
    try:
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='body']")))   
    except:
        print('Webdriver Wait Timeout')
    
    print('going to promotion page...')
    
    promotionCodeURL = 'https://www.tindie.com/promotions/create/'
    
    driver.get(promotionCodeURL)
    
    try:
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='id_max_item_purchase']")))   
    except:
        print('Webdriver Wait Timeout')
    
    descriptionInput = driver.find_element(by=By.XPATH, value="//*[@id='id_description']")
    descriptionInput.send_keys('happyhamburger')
    
    time.sleep(1)
    
    try:
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='id_submit']")))   
    except:
        print('Webdriver Wait Timeout')
        
    time.sleep(1)
        
    button2 = driver.find_element(by=By.XPATH, value="//*[@id='id_submit']")
    driver.execute_script("arguments[0].scrollIntoView();", button2)
    
    time.sleep(1)
    button2.click()
    
    newHeaders = ''
    useragent = ''
    
    for request in driver.requests:

            
        if (request.url == 'https://www.tindie.com/promotions/create/' and 'csrfmiddlewaretoken' in request.body.decode()):
            
            cookieSearch = str(request.headers).splitlines()
            
            for line in cookieSearch:
                #print('LINE', line)
                if ('cookie' in line):
                    tindieCookie = line.split('cookie: ')[1]
                    newHeaders = request.headers
                    
                    try:
                        csrftoken = line.split('csrftoken=')[1]
                        csrftoken = csrftoken.split(';')[0]
                        sessionid = line.split('sessionid=')[1]
                        sessionid = sessionid.split(';')[0]
                    except:
                        print('Error getting cookie')
                    
                    cookieFound = True
                    #break
                if ('user-agent' in line):
                    try:
                        useragent = line.split('user-agent: ')[1]
                    except:
                        useragent = ''
            
            requestPayload = request.body.decode()
            
            csrfMiddleWareToken = requestPayload.split('csrfmiddlewaretoken=')[1]
            csrfMiddleWareToken = csrfMiddleWareToken.split('&')[0]
            
            if (cookieFound == True):
                break

    tindieCookie = str(tindieCookie)
    
    tindieCookieJSON = {
        "tindieCookie": tindieCookie,
        "csrfToken": csrftoken,
        "sessionid": sessionid,
        "csrfMiddleWareToken": csrfMiddleWareToken,
        "userAgent": useragent,
        "dateTime": time.strftime('%Y%m%d_%H%M%S')
    }

    with open('tindieCookie.json', 'w') as outfile:
        json.dump(tindieCookieJSON, outfile, indent=4)
    
    #print('Waiting for 1 second')
    time.sleep(1)
    
    driver.quit()
    print('Tindie Cookie Updated on', time.strftime('%Y-%m-%d %H:%M:%S'))
    return


###############################################################################


tindieCookieDelta = 5 #days

with open("tindieCookie.json", 'r') as f:
    cookieDetails = json.load(f)
    cookieDateTimeStamp = cookieDetails['dateTime']
    
    if (datetime.now() - datetime.strptime(cookieDateTimeStamp, '%Y%m%d_%H%M%S')) > timedelta(days=tindieCookieDelta):
        print('Tindie Cookie is expired', 'Getting new cookie...', datetime.strptime(cookieDateTimeStamp, '%Y%m%d_%H%M%S'))
        getNewTindieCookie()
        print('Resuming program...')
    else:
        #print('Tindie Cookie is still valid... using existing cookie')
        pass
    
###############################################################################

#getNewTindieCookie()

