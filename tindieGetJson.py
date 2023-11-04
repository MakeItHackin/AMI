
import requests
import time
from datetime import datetime, timedelta
import traceback
import json

import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

tindie_username = os.getenv('tindie_username')
tindie_api_key = os.getenv('tindie_api_key')

displayShipped = 'false'
limit = '500'
offset = '0'

url = 'https://www.tindie.com/api/v1/order/?format=json&username=' + tindie_username + '&api_key=' + tindie_api_key + '&shipped=' + displayShipped + '&limit=' + limit + '&offset=' + offset

def getNewOrders():
    
    tindieCombinedOrders = []
    
    try:
        print('Getting Tindie Orders...')
        orders = requests.get(url)
        orderList = orders.json()
        pretty_json = json.dumps(orderList, indent=4)
        orderCount = orderList['meta']['total_count']
        print('Order Count: ' + str(orderCount))
        customerOrders = orderList['orders']
        productsToExclude = []
        customOrder = False
        waitingForInstructions = False
        newOrderShippingStreet3 = ''

        for newOrder in customerOrders:
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

            newOrderCompany = newOrder['company_title']
            newOrderDate = newOrder['date']
            newOrderDateShipped = newOrder['date_shipped']
            newOrderDiscountCode = newOrder['discount_code']
            newOrderEmail = newOrder['email']
            newOrderItems = newOrder['items']
            
            newOrderMessage = newOrder['message']
            newOrderNumber = str(newOrder['number'])
            newOrderPayment = newOrder['payment']
            newOrderPhone = newOrder['phone']
            newOrderRefunded = newOrder['refunded']
            newOrderShipped = newOrder['shipped']
            newOrderShippingCity = newOrder['shipping_city']
            newOrderShippingCountry = newOrder['shipping_country']
            newOrderShippingCountryCode = newOrder['shipping_country_code']
            newOrderShippingInstructions = newOrder['shipping_instructions']  
            newOrderCustomerName = newOrder['shipping_name']
            buyerFirstName = newOrderCustomerName.split(" ")[0]
            newOrderShippingPostalCode = newOrder['shipping_postcode']
            newOrderShippingService = newOrder['shipping_service']  
            newOrderShippingService = newOrderShippingService.split("United States Postal Service ")[1]
            newOrderShippingState = newOrder['shipping_state']
            newOrderShippingStreet = newOrder['shipping_street']
            streetLines = newOrderShippingStreet.splitlines()
            streetLineAmount = len(streetLines)
            if (streetLineAmount > 1):
                newOrderShippingStreet = ''
                streetIndex = 0
                for line in streetLines:
                    if (streetIndex == 0):
                        newOrderShippingStreet = line
                        newOrderShippingStreet1 = line
                    elif (streetIndex == 1):
                        newOrderShippingStreet2 = line
                    elif (streetIndex == 2):
                        newOrderShippingStreet3 = line
                    else:
                        newOrderShippingStreet = newOrderShippingStreet + ' ' + line
                    streetIndex += 1

            else:
                newOrderShippingStreet1 = newOrderShippingStreet
                newOrderShippingStreet2 = ''
                newOrderShippingStreet3 = ''
            newOrderShippingStreet = newOrderShippingStreet.replace(","," ")    
            newOrderTrackingCode = newOrder['tracking_code']
            newOrderTrackingURL = newOrder['tracking_url']

            paymentTotal = newOrder['total_subtotal']
            shippingTotal = newOrder['total_shipping']

            orderJson['order_id'] = newOrderNumber
            orderJson['buyer_email'] = newOrderEmail
            orderJson['buyer_name'] = newOrderCustomerName
            orderJson['recipient_name'] = newOrderCustomerName
            orderJson['buyer_is_repeat'] = False
            if (newOrderShipped == True):
                orderJson['order_state'] = 'Complete'
            else:
                orderJson['order_state'] = 'New'
            orderJson['order_notes'] = newOrderShippingInstructions
            orderJson['order_is_gift'] = False
            orderJson['order_gift_message'] = ''
            orderJson['order_has_unread_message'] = False
            orderJson['order_payment_total'] = '$' + "{:.2f}".format(paymentTotal) 
            orderJson['order_tax_total'] = '$' + "{:.2f}".format(0) 
            orderJson['order_shipping_total'] = '$' + "{:.2f}".format(shippingTotal) 
            
            orderJson['order_shipping_method'] = newOrderShippingService

            orderDate = datetime.strptime(newOrderDate, '%Y-%m-%dT%H:%M:%S.%f')
            orderDate = orderDate.strftime('%B %d, %Y')

            orderJson['order_date'] = orderDate
            shipByDate = datetime.strptime(orderDate, '%B %d, %Y')
            shipByDate = shipByDate + timedelta(days=13)
            shipByDate = shipByDate.strftime('%B %d, %Y')

            shipByDate = 'Ship By: ' + shipByDate

            orderJson['ship_by_date'] = shipByDate
            orderJson['platform'] = 'tindie'

            orderJson['buyer_phone'] = newOrderPhone
            orderJson['buyer_address1'] = newOrderShippingStreet1
            orderJson['buyer_address2'] = newOrderShippingStreet2
            orderJson['buyer_address3'] = newOrderShippingStreet3
            orderJson['buyer_city'] = newOrderShippingCity
            orderJson['buyer_state_province'] = newOrderShippingState
            orderJson['buyer_postal_code'] = newOrderShippingPostalCode
            orderJson['buyer_country'] = newOrderShippingCountry
            orderJson['buyer_company'] = ''
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
                
                itemModelNumber = items['model_number']
                itemOptions = items['options'] 
                itemPreOrder = items['pre_order']
                itemPriceTotal = items['price_total']
                completeItemTotal += itemPriceTotal
                itemPriceUnit = items['price_unit']
                itemPoductName = items['product']
                itemOptions = items['options']
                itemQuantity = items['quantity']
                totalItemQuantity += itemQuantity
                itemProductNumber = items['sku'] 
                itemStatus = items['status']
                if ("Default" not in itemOptions):
                    if ("Customized" in itemOptions):
                        customOrder = True
                        if (newOrderShippingInstructions == ''):
                            waitingForInstructions = True
                if (itemProductNumber not in productsToExclude):
                    if (waitingForInstructions == True):
                        print("CUSTOM ORDER BUT NO INSTRUCTIONS - MATCH",newOrderNumber,itemPoductName,itemProductNumber,itemStatus)
                        personalized_ordered_with_no_instructions = True
                    else:
                        print("MATCH !!!",newOrderNumber,itemPoductName,itemProductNumber,itemStatus)
                    itemMatchBool = True
                else:
                    print("PRODUCT EXCLUDED ---> ",newOrderNumber,itemPoductName,itemProductNumber,itemStatus)
                    itemExcluded = True

                orderJson['personalized_ordered_with_no_instructions'] = personalized_ordered_with_no_instructions

                orderJson['order_items_total'] = '$' + "{:.2f}".format(completeItemTotal) 

                productOrdered = itemPoductName
                productQuantity = itemQuantity
                
                if ('Default or Custom' in itemOptions):
                    productType = itemOptions.split(': ')[1]
                    productType = productType.split(' (')[0]
                else:
                    productType = itemOptions
                personalization = ''
                orderJson['products'].append({'product_name': productOrdered, 'product_quantity': productQuantity, 'product_type': productType, 'personalization': personalization})

            orderJson['total_item_quantity'] = totalItemQuantity
            orderJson['is_custom_order'] = customOrder

            itemAmount = len(newOrderItems)
            
            
            ##########################################################
            ##  BELOW IS THE NEW PART
            ##########################################################

            #SINCE TINDIE DOESN'T DO TAXES, SET THESE TO FALSE
            orderJson['default_ordered_with_personalization'] = False
            orderJson['canadian_tax'] = ''
            orderJson['display_canadian_tax'] = False
            orderJson['display_euro_vat_tax'] = False
            orderJson['display_uk_vat_tax'] = False
            orderJson['display_canada_zero_rated_tax'] = False
            orderJson['vat_tax_paid'] = 0
            orderJson['vat_currency_code'] = ''
            
            jsonFileName = f"tindie_orderDetails-{orderJson['order_id']}.json"
            if not os.path.exists(jsonFileName):
                #print('file does not exist, saving file...')
                with open(jsonFileName, 'w') as file:
                #print('saving file...')
                    json.dump(orderJson, file, indent=4)
            
            #print(orderDetails['products'][0])
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
                tindieCombinedOrders.append(dict3)

            with open('tindie_orders_in_json.json', 'w') as file:
                #print('saving file...')
                json.dump(tindieCombinedOrders, file, indent=4)
            
    except Exception as e:
        print('Error on Tindie JSON Orders: ', e)
        traceback.print_exc()
        
    print("DONE!")
    print('##################################################################')
    return(tindieCombinedOrders)