
import requests
import time
from datetime import datetime, timedelta
import traceback
import json

import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

lectronz_bearer_token = os.getenv('lectronz_bearer_token')
exchange_rate_api_key = os.getenv('exchange_rate_api_key')

###############################################################################

def getExchangeRate():
    conversionRate = 0
    try:
        exchange_url = f"https://v6.exchangerate-api.com/v6/{exchange_rate_api_key}/pair/EUR/USD/"
        response = requests.get(exchange_url)
        data = response.json()
        if (data['result'] == 'success'):
            conversionRate = data['conversion_rate']
            print('SUCCESS GETTING EXHANGE RATE FOR EUR to USD:', conversionRate)
        else:
            print('ERROR GETTING EXHANGE RATE')
    except:
        print('ERROR GETTING EXHANGE RATE 2')
    return(conversionRate)
    
###############################################################################

def state_name_to_abbreviation(state_name):
    state_abbreviations = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
        'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
        'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
        'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
    }
    
    # Convert input state name to title case for accurate matching
    formatted_state_name = state_name.title()
    
    # Check if the state name is in the dictionary
    if formatted_state_name in state_abbreviations:
        return state_abbreviations[formatted_state_name]
    else:
        return "Invalid State Name"

def getNewOrders(exchangeRateForLectronz):
    
    url = 'https://lectronz.com/api/v1/orders' 
    
    lectronzCombinedOrders = []
    
    try:
        print('Getting Lectronz Orders...')
        
        payload={}
        headers = {
        'Authorization': 'Bearer '+ lectronz_bearer_token
        }       

        orders = requests.request("GET", url, headers=headers, data=payload)
        orderList = orders.json()
        pretty_json = json.dumps(orderList, indent=4)
        customerOrders = orderList['orders']
        productsToExclude = []
        customOrder = False
        waitingForInstructions = False
        newOrderShippingStreet3 = ''

    ############################################################################################

        orderCount = 0
        
        for newOrder in customerOrders:
            if (newOrder['status'] != 'payment_success'):
                continue
            orderCount += 1 
        
        print('Total Order Count: ' + str(orderCount))
        
        for newOrder in customerOrders:
            
            if (newOrder['status'] != 'payment_success'):
                continue
            
            orderCount += 1 
            
            orderJson = {
            "order_id": '',
            "buyer_email": '',
            "buyer_name": '',
            "buyer_is_repeat": '',
            "order_state": '',
            "order_notes": '',
            "private_notes": '',
            "order_is_gift": '',
            "order_gift_message": '',
            "order_has_unread_message": '',
            "order_payment_total": '',
            "order_tax_total": '',
            "order_shipping_total": '',
            "order_items_total": '',
            "order_shipping_method": '',
            "order_shipping_mail_class": '',
            "products":[],
            "order_date": '',
            "ship_by_date": '',
            "platform": '',
            "order_id": '',
            'canadian_tax': '',
            'display_canadian_tax': '',
            'display_euro_vat_tax': '',
            'display_uk_vat_tax': '',
            'display_canada_zero_rated_tax': '',
            'vat_tax_paid': '',
            'vat_currency_code': '',
            'buyer_phone': '',
            'recipient_name': '',
            'buyer_address1': '',
            'buyer_address2': '',
            'buyer_address3': '',
            'buyer_city': '',
            'buyer_state_province': '',
            'buyer_postal_code': '',
            'buyer_country': '',
            'buyer_company': '',
            'buyer_country_code': '',
            'total_item_quantity': '',
            'is_international': '',
            'is_custom_order': '',
            'default_ordered_with_personalization': '',
            'personalized_ordered_with_no_instructions': '',
            'shopify_order_id': None                 
            }

            newOrderCompany = newOrder['shipping_address']['organization']
            newOrderDate = newOrder['created_at']
            newOrderEmail = newOrder['customer_email']
            newOrderItems = newOrder['items']
            newOrderMessage = newOrder['customer_note']
            newOrderNumber = str(newOrder['id'])
            newOrderPayment = newOrder['payment']
            newOrderPhone = newOrder['customer_phone']
            newOrderShippingCity = newOrder['shipping_address']['city']
            newOrderShippingCountry = newOrder['shipping_address']['country']
            newOrderShippingCountryCode = newOrder['shipping_address']['country_code']
            newOrderShippingInstructions = newOrder['customer_note']  
            newOrderCustomerName = newOrder['shipping_address']['first_name'] + ' ' + newOrder['shipping_address']['last_name']
            buyerFirstName = newOrder['shipping_address']['first_name']
            newOrderShippingPostalCode = newOrder['shipping_address']['postal_code']
            newOrderShippingService = newOrder['shipping_method']  
            newOrderShippingState = newOrder['shipping_address']['state']
            newOrderShippingState = state_name_to_abbreviation(newOrderShippingState)
            newOrderShippingStreet1 = ''
            newOrderShippingStreet2 = ''
            newOrderShippingStreet3 = ''
            newOrderShippingStreet1 = newOrder['shipping_address']['street'] 
            newOrderShippingStreet2 = newOrder['shipping_address']['street_extension']
            newOrderTrackingCode = newOrder['tracking_code']
            newOrderTrackingURL = newOrder['tracking_url']
            paymentTotal = newOrder['total']
            shippingTotal = newOrder['shipping_cost']
            taxtotal = newOrder['total_tax']
            paymentTotal = paymentTotal * exchangeRateForLectronz #convert to USD
            shippingTotal = shippingTotal * exchangeRateForLectronz #convert to USD
            taxtotal = taxtotal * exchangeRateForLectronz #convert to USD
            orderJson['order_id'] = newOrderNumber
            orderJson['buyer_email'] = newOrderEmail
            orderJson['buyer_name'] = newOrderCustomerName
            orderJson['recipient_name'] = newOrderCustomerName
            orderJson['buyer_is_repeat'] = False

            if (newOrderTrackingCode != ''):
                orderJson['order_state'] = 'Complete'
            else:
                orderJson['order_state'] = 'New'
            orderJson['order_notes'] = newOrderShippingInstructions
            orderJson['order_is_gift'] = False
            orderJson['order_gift_message'] = ''
            orderJson['order_has_unread_message'] = False
            orderJson['order_payment_total'] = '$' + "{:.2f}".format(paymentTotal) #+ str(paymentTotal)
            orderJson['order_tax_total'] = '$' + "{:.2f}".format(taxtotal) #+ str(0)
            orderJson['order_shipping_total'] = '$' + "{:.2f}".format(shippingTotal) #+ str(shippingTotal)
            
            orderJson['order_shipping_method'] = newOrderShippingService
            
            orderDate = datetime.strptime(newOrderDate, '%Y-%m-%dT%H:%M:%S.%fZ')
            orderDate = orderDate.strftime('%B %d, %Y')

            orderJson['order_date'] = orderDate

            shipByDate = newOrder['fulfill_until']
            
            shipByDate = datetime.strptime(shipByDate, '%Y-%m-%dT%H:%M:%S.%fZ')
            shipByDate = shipByDate.strftime('%B %d, %Y')

            shipByDate = 'Ship By: ' + shipByDate
            orderJson['ship_by_date'] = shipByDate
            orderJson['platform'] = 'lectronz'

            orderJson['buyer_phone'] = newOrderPhone
            orderJson['buyer_address1'] = newOrderShippingStreet1
            orderJson['buyer_address2'] = newOrderShippingStreet2
            orderJson['buyer_address3'] = newOrderShippingStreet3
            orderJson['buyer_city'] = newOrderShippingCity
            orderJson['buyer_state_province'] = newOrderShippingState
            orderJson['buyer_postal_code'] = newOrderShippingPostalCode
            orderJson['buyer_country'] = newOrderShippingCountry
            orderJson['buyer_company'] = newOrderCompany
            orderJson['buyer_country_code'] = newOrderShippingCountryCode
            
            if (newOrderShippingCountryCode != 'US'):
                orderJson['is_international'] = True
            else:
                orderJson['is_international'] = False
            
            personalized_ordered_with_no_instructions = False
            itemExcluded = False
            
            totalItemQuantity = 0
            
            completeItemTotal = 0
            
            for items in newOrderItems:
                itemIndex = 0

                itemOptions = items['options'] #default or custom
                itemPriceTotal = items['price']
                completeItemTotal += itemPriceTotal
                itemPoductName = items['product_name']
                itemOptions = items['options']
                itemQuantity = items['quantity']
                totalItemQuantity += itemQuantity
                itemProductNumber = items['product_id']  #this is the product number
                if ("Default" not in itemOptions):
                    if ("Customized" in itemOptions):
                        customOrder = True
                        if (newOrderShippingInstructions == ''):
                            waitingForInstructions = True
                if (itemProductNumber not in productsToExclude):
                    if (waitingForInstructions == True):
                        print("CUSTOM ORDER BUT NO INSTRUCTIONS - MATCH",newOrderNumber,itemPoductName,itemProductNumber)
                        personalized_ordered_with_no_instructions = True
                    else:
                        print("MATCH !!!",newOrderNumber,itemPoductName,itemProductNumber)
                    itemMatchBool = True
                else:
                    print("PRODUCT EXCLUDED ---> ",newOrderNumber,itemPoductName,itemProductNumber)
                    itemExcluded = True

                orderJson['personalized_ordered_with_no_instructions'] = personalized_ordered_with_no_instructions

                completeItemTotal = completeItemTotal * exchangeRateForLectronz #convert to USD
                
                orderJson['order_items_total'] = '$' + "{:.2f}".format(completeItemTotal) #str(completeItemTotal)

                productOrdered = itemPoductName
                productQuantity = itemQuantity

                if ('Default or Custom' in itemOptions):
                    productType = itemOptions.split(': ')[1]
                    productType = productType.split(' (')[0]
                else:
                    try:
                        productType = ''
                        for option in itemOptions:
                            if (productType == ''):
                                productType = option['name'] + ' - ' + option['choice'] 
                            else:
                                productType = productType + '\n' + option['name'] + ' - ' + option['choice']
                    except:
                        productType = itemOptions
                
                if (len(productType) == 0):
                    productType = ''
                personalization = ''
                orderJson['products'].append({'product_name': productOrdered, 'product_quantity': productQuantity, 'product_type': productType, 'personalization': personalization})

            orderJson['total_item_quantity'] = totalItemQuantity
            orderJson['is_custom_order'] = customOrder

            itemAmount = len(newOrderItems)
            
            
            ##########################################################
            ##  BELOW IS THE NEW PART
            ##########################################################

            #SINCE LECTRONZ DOESN'T DO TAXES, SET THESE TO FALSE
            orderJson['default_ordered_with_personalization'] = False
            orderJson['canadian_tax'] = ''
            orderJson['display_canadian_tax'] = False
            orderJson['display_euro_vat_tax'] = False
            orderJson['display_uk_vat_tax'] = False
            orderJson['display_canada_zero_rated_tax'] = False
            orderJson['vat_tax_paid'] = 0
            orderJson['vat_currency_code'] = ''
            
            jsonFileName = f"lectronz_orderDetails-{orderJson['order_id']}.json"
            if not os.path.exists(jsonFileName):
                #print('file does not exist, saving file...')
                with open(jsonFileName, 'w') as file:
                #print('saving file...')
                    json.dump(orderJson, file, indent=4)
            
            numberOfProducts = len(orderJson['products'])
            orderJson['order_state'] = str(orderJson['order_state'])
            
            newShipByDate = orderJson['ship_by_date'].replace('Ship By: ', '')
            newShipByDate = newShipByDate.strip()
            newShipByDate = datetime.strptime(newShipByDate, '%B %d, %Y')
            newShipByDate = newShipByDate.strftime('%m/%d/%Y')
            orderJson['ship_by_date'] = newShipByDate
            
            newOrderDate = orderJson['order_date'].strip()
            newOrderDate = datetime.strptime(newOrderDate, '%B %d, %Y')
            newOrderDate = newOrderDate.strftime('%m/%d/%Y')
            orderJson['order_date'] = newOrderDate
            
            for i in range(numberOfProducts):

                flattenedDetails = {**orderJson}
                orderNumber = flattenedDetails['order_id']
                if (numberOfProducts > 1):
                    flattenedDetails['order_id'] = f"{orderNumber}-MULTI-{i+1}"
                singleProduct = orderJson['products'][i]
                dict3 = {**flattenedDetails, **singleProduct}
                del dict3['products'] 
                lectronzCombinedOrders.append(dict3)
                
            with open('lectronz_orders_in_json.json', 'w') as file:
                json.dump(lectronzCombinedOrders, file, indent=4)
            
    except Exception as e:
        print('Error on LECTRONZ JSON Orders: ', e)
        traceback.print_exc()

    print("DONE!")
    print('##################################################################')
    return(lectronzCombinedOrders)

#getNewOrders()