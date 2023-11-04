
import requests
from datetime import datetime, timedelta
import json
import traceback
import platformFunctions

import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

shopify_access_token = os.getenv('shopify_access_token')

###############################################################################

status_to_get = 'unfulfilled'

url = f"https://your-store-name.myshopify.com/admin/api/2023-01/orders.json?status={status_to_get}"

def getNewOrders():
    
    shopifyCombinedOrders = []
    
    try:
        print('Getting Shopify Orders...')
        payload={}
        headers = {
        'X-Shopify-Access-Token': shopify_access_token
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        json_response = response.json()
        #print('##################################################################')
        #print(json_response)
        #print('##################################################################')
        pretty_json = json.dumps(json_response, indent=4)
        #print(pretty_json)

        orders = json_response['orders']
        
        print('Total Order Count:', len(orders))
        
        for order in orders:
            print('##################################################################')
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
            

            shopifyOrderId = order['id']
            orderJson['shopify_order_id'] = order['id']
            orderNumber = order['order_number']
                
            orderJson['order_id'] = str(orderNumber)
            orderJson['buyer_email'] = order['contact_email']
            orderJson['recipient_name'] = order['shipping_address']['first_name'] + ' ' + order['shipping_address']['last_name']
            orderJson['buyer_name'] = order['customer']['first_name'] + ' ' + order['customer']['last_name']
            orderJson['buyer_is_repeat'] = False
            if (order['fulfillment_status'] == 'fulfilled'):
                orderJson['order_state'] = 'Completed'
            else: 
                orderJson['order_state'] = 'New'
            #orderJson['order_notes'] = order['note']
            buyerNotes = order['note']
            if (buyerNotes is None):
                orderJson['order_notes'] = ''
            else:
                orderJson['order_notes'] = buyerNotes
            orderJson['order_is_gift'] = False
            orderJson['order_gift_message'] = ''
            orderJson['order_has_unread_message'] = False
            orderJson['order_payment_total'] = order['current_total_price']
            orderJson['order_tax_total'] = order['total_tax']
            orderJson['order_shipping_total'] = order['shipping_lines'][0]['price']
            orderJson['order_shipping_method'] = order['shipping_lines'][0]['title']  #"source": "usps", "title": "First Class Package", "Priority Mail", "Priority Mail Express"
            order_date = order['created_at']
            
            order_date = datetime.strptime(order_date, '%Y-%m-%dT%H:%M:%S%z')
            order_date = order_date.strftime('%B %d, %Y')
            
            orderJson['order_date'] = order_date
            
            #orderJson['ship_by_date'] = 
            orderJson['platform'] = 'mih'
            orderJson['buyer_phone'] = order['phone']
            if order['phone'] is None:
                orderJson['buyer_phone'] = ''
            orderJson['buyer_address1'] = order['shipping_address']['address1']
            orderJson['buyer_address2'] = order['shipping_address']['address2'] #can be null
            if order['shipping_address']['address2'] is None:
                orderJson['buyer_address2'] = ''
            
            orderJson['buyer_address3'] = '' 
            orderJson['buyer_city'] = order['shipping_address']['city']
            orderJson['buyer_state_province'] = order['shipping_address']['province_code']  #province code is two letter.  province is full name
            orderJson['buyer_postal_code'] = order['shipping_address']['zip']  
            orderJson['buyer_country'] = order['shipping_address']['country']
            orderJson['buyer_company'] = order['shipping_address']['company']  #can be null
            if order['shipping_address']['company'] is None:
                orderJson['buyer_company'] = ''
            
            orderJson['buyer_country_code'] = order['shipping_address']['country_code']
            
            if (order['shipping_address']['country_code'] == 'US'):
                orderJson['is_international'] = False
            else:
                orderJson['is_international'] = True
            
            
            orderJson['order_items_total'] = order['current_subtotal_price']
            
            try:
                ship_by_date = platformFunctions.getShopifyFulfillmentOrder(shopifyOrderId)
                #print('ship_by_date1', ship_by_date)
                ship_by_date = datetime.strptime(ship_by_date, '%Y-%m-%dT%H:%M:%S%z')
                #print('ship_by_date2', ship_by_date)
                ship_by_date = ship_by_date.strftime('%B %d, %Y')
                #print('ship_by_date3', ship_by_date)
            except:
                ship_by_date = ''
                #print('ship_by_date4', ship_by_date)

            ship_by_date = 'Ship By: ' + ship_by_date
            
            orderJson['ship_by_date'] = ship_by_date
            
            if (order['financial_status'] == 'paid'):
                #print('order has been paid')
                pass

            totalItemQuantity = 0
            customOrder = False
            default_ordered_with_personalization = False
            personalized_ordered_with_no_instructions = False
            productType = ''
            
            for products in order['line_items']:
                productOrdered = products['title']
                productQuantity = products['quantity']
                productType = products['variant_title']
                try:
                    if ('custom' in productType.lower()):
                        customOrder = True
                    if ('default' in productOrdered.lower() and buyerNotes != ''):
                        default_ordered_with_personalization = True
                except:
                    pass
                if productType is None:    
                    productType = ''
                personalization = ''
                totalItemQuantity += productQuantity
                orderJson['products'].append({'product_name': productOrdered, 'product_quantity': productQuantity, 'product_type': productType, 'personalization': personalization})
                
            orderJson['total_item_quantity'] = totalItemQuantity
            
            if (buyerNotes == '' and customOrder == True):
                personalized_ordered_with_no_instructions = True

            orderJson['personalized_ordered_with_no_instructions'] = personalized_ordered_with_no_instructions
            orderJson['default_ordered_with_personalization'] = default_ordered_with_personalization
            
            buyerFirstName = order['shipping_address']['first_name']
            
            orderJson['is_custom_order'] = customOrder
            
            ##########################################################
            ##  BELOW IS THE NEW PART
            ##########################################################

            #SINCE SHOPIFY DOESN'T DO TAXES, SET THESE TO FALSE
            orderJson['default_ordered_with_personalization'] = False
            orderJson['canadian_tax'] = ''
            orderJson['display_canadian_tax'] = False
            orderJson['display_euro_vat_tax'] = False
            orderJson['display_uk_vat_tax'] = False
            orderJson['display_canada_zero_rated_tax'] = False
            orderJson['vat_tax_paid'] = 0
            orderJson['vat_currency_code'] = ''
            
            jsonFileName = f"mih_orderDetails-{orderJson['order_id']}.json"
            if not os.path.exists(jsonFileName):
                with open(jsonFileName, 'w') as file:
                #print('saving file...')
                    json.dump(orderJson, file, indent=4)
                    
            numberOfProducts = len(orderJson['products'])
            orderJson['order_state'] = str(orderJson['order_state'])
            
            newShipByDate = orderJson['ship_by_date'].replace('Ship By: ', '')
            newShipByDate = newShipByDate.strip()
            if (newShipByDate != ''):
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
                shopifyCombinedOrders.append(dict3)

            with open('shopify_orders_in_json.json', 'w') as file:
                json.dump(shopifyCombinedOrders, file, indent=4)
                    
    except Exception as e:
        print('ERROR GETTING SHOPIFY ORDERS', e)
        traceback.print_exc()
    print("DONE!")
    print('##################################################################')
    return(shopifyCombinedOrders)
    
#getNewOrders()