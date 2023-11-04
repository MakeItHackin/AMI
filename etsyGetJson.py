import requests
import json
import traceback
from datetime import datetime
import platformFunctions

#import datetime
import pytz

import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

etsy_shop_id = os.getenv('etsy_shop_id')
etsy_client_id = os.getenv('etsy_client_id')


###############################################################################


countryNameList = ["Afghanistan", "Aland Islands", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla", "Antarctica", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bahamas", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia, Plurinational State of", "Bonaire, Sint Eustatius and Saba", "Bosnia and Herzegovina", "Botswana", "Bouvet Island", "Brazil", "British Indian Ocean Territory", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Cayman Islands", "Central African Republic", "Chad", "Chile", "China", "Christmas Island", "Cocos (Keeling) Islands", "Colombia", "Comoros", "Congo", "Congo, the Democratic Republic of the", "Cook Islands", "Costa Rica", "CÃ´te d'Ivoire", "Croatia", "Cuba", "CuraÃ§ao", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Falkland Islands (Malvinas)", "Faroe Islands", "Fiji", "Finland", "France", "French Guiana", "French Polynesia", "French Southern Territories", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada", "Guadeloupe", "Guam", "Guatemala", "Guernsey", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Heard Island and McDonald Islands", "Holy See (Vatican City State)", "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran, Islamic Republic of", "Iraq", "Ireland", "Isle of Man", "Israel", "Italy", "Jamaica", "Japan", "Jersey", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, Democratic People's Republic of", "Korea, Republic of", "Kuwait", "Kyrgyzstan", "Lao People's Democratic Republic", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macao", "Macedonia, the Former Yugoslav Republic of", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Martinique", "Mauritania", "Mauritius", "Mayotte", "Mexico", "Micronesia, Federated States of", "Moldova, Republic of", "Monaco", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue", "Norfolk Island", "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau", "Palestine, State of", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Pitcairn", "Poland", "Portugal", "Puerto Rico", "Qatar", "RÃ©union", "Romania", "Russian Federation", "Rwanda", "Saint BarthÃ©lemy", "Saint Helena, Ascension and Tristan da Cunha", "Saint Kitts and Nevis", "Saint Lucia", "Saint Martin (French part)", "Saint Pierre and Miquelon", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Sint Maarten (Dutch part)", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Georgia and the South Sandwich Islands", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Svalbard and Jan Mayen", "Swaziland", "Sweden", "Switzerland", "Syrian Arab Republic", "Taiwan, Province of China", "Tajikistan", "Tanzania, United Republic of", "Thailand", "Timor-Leste", "Togo", "Tokelau", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Turks and Caicos Islands", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "United States Minor Outlying Islands", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela, Bolivarian Republic of", "Viet Nam", "Virgin Islands, British", "Virgin Islands, U.S.", "Wallis and Futuna", "Western Sahara", "Yemen", "Zambia", "Zimbabwe"]
countryCodeList = ["AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ", "BH", "BS", "BD", "BB", "BY", "BE", "BZ", "BJ", "BM", "BT", "BO", "BQ", "BA", "BW", "BV", "BR", "IO", "BN", "BG", "BF", "BI", "KH", "CM", "CA", "CV", "KY", "CF", "TD", "CL", "CN", "CX", "CC", "CO", "KM", "CG", "CD", "CK", "CR", "CI", "HR", "CU", "CW", "CY", "CZ", "DK", "DJ", "DM", "DO", "EC", "EG", "SV", "GQ", "ER", "EE", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF", "GA", "GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "GW", "GY", "HT", "HM", "VA", "HN", "HK", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP", "JE", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MK", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU", "YT", "MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MP", "NO", "OM", "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR", "QA", "RE", "RO", "RU", "RW", "BL", "SH", "KN", "LC", "MF", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG", "SX", "SK", "SI", "SB", "SO", "ZA", "GS", "SS", "ES", "LK", "SD", "SR", "SJ", "SZ", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH", "TL", "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "US", "UM", "UY", "UZ", "VU", "VE", "VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW"] 

###############################################################################

def etsyGetReceipts():
    etsy_access_token = platformFunctions.getNewEtsyAccessToken()

    url = f"https://api.etsy.com/v3/application/shops/{etsy_shop_id}/receipts?was_shipped=false&was_canceled=false&was_paid=true"
    #url = f"https://api.etsy.com/v3/application/shops/{etsy_shop_id}/receipts?was_shipped=true&limit=25" #
    payload={}
    headers = {
        "x-api-key": etsy_client_id,
        "Authorization": 'Bearer ' + etsy_access_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    #print(response.text)
    #print(response.json()) # this will print the JSON response from the API call


    json_response = response.json()
    #print('##################################################################')
    #print(json_response)
    #print('##################################################################')
    pretty_json = json.dumps(json_response, indent=4)
    #print(pretty_json)


    #json_object = json.loads(data)

    # Open a new file in write mode
    ###with open('output.json', 'w') as file:
        # Write the Python object to the file in JSON format
    ###    json.dump(json_response, file, indent=4)
    
    return(json_response)
    
###############################################################################


def getNewOrders(): #include_completed, amount_completed, amount_offset
    
    print('##################################################################')
    print('Getting Etsy Orders...')
    try:
        #etsyGetReceipts()

        #with open('output.json') as file:
        #    etsy_file = json.load(file)

        etsy_file = etsyGetReceipts()
        
        etsy_results = etsy_file['results']
        etsy_order_count = etsy_file['count']
            
        print('Total Order Count: ' + str(etsy_order_count))
        
        etsyCombinedOrders = []
        
        for result in etsy_results:
            
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
        
            orderID = result['receipt_id']
            orderID = str(orderID)
            buyerEmail = result['buyer_email']
            buyerName = result['name']
            isBuyerRepeat = False #not sure if this informatin is available
            isGift = result['is_gift']
            giftMessage = result['gift_message']
            paymentTotal = result['grandtotal']['amount']/100
            taxTotal = result['total_tax_cost']['amount']/100
            shippingTotal = result['total_shipping_cost']['amount']/100
            itemsTotal = result['subtotal']['amount']/100
            shippingMethod = result['transactions'][0]['shipping_upgrade']
            #shippingMailClass = result['transactions']['mail_class']
            orderDate = result['created_timestamp']
            canadianTax = result['total_vat_cost']['amount']/100
            vat_tax_paid = result['total_vat_cost']['amount']/100
            display_canadian_tax = False #need to update
            display_euro_vat_tax = False #need to update
            display_uk_vat_tax = False #need to update
            display_canada_zero_rated_tax = False #need to update
            vat_currency_code = result['total_vat_cost']['currency_code']
            buyerNotes = result['message_from_buyer']
            if buyerNotes == None:
                buyerNotes = ''
            
            expected_ship_date = result['transactions'][0]['expected_ship_date']
                
            #epoch_time = 1680637899

            # Define the Central Time Zone
            central_tz = pytz.timezone('US/Central')

            # Convert epoch time to datetime object
            utc_datetime = datetime.utcfromtimestamp(expected_ship_date)

            # Convert UTC datetime to Central Time Zone
            central_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(central_tz)

            # Print the local datetime in Central Time Zone
            
            expected_ship_date = central_datetime.strftime('%B %d, %Y')
            
            orderJson['ship_by_date'] = 'Ship By: ' + expected_ship_date
            

            order_date_utc_datetime = datetime.utcfromtimestamp(orderDate)

            # Convert UTC datetime to Central Time Zone
            order_date_central_datetime = order_date_utc_datetime.replace(tzinfo=pytz.utc).astimezone(central_tz)

            # Print the local datetime in Central Time Zone
            
            orderDate = order_date_central_datetime.strftime('%B %d, %Y')
            
            orderJson['order_id'] = orderID
            orderJson['buyer_email'] = buyerEmail
            orderJson['buyer_name'] = buyerName
            orderJson['buyer_is_repeat'] = isBuyerRepeat
            ###orderJson['order_state'] = orderState
            orderJson['order_notes'] = buyerNotes
            orderJson['order_is_gift'] = isGift
            orderJson['order_gift_message'] = giftMessage
            ###orderJson['order_has_unread_message'] = hasUnreadMessage
            orderJson['order_payment_total'] = paymentTotal
            orderJson['order_tax_total'] = taxTotal
            orderJson['order_shipping_total'] = shippingTotal
            orderJson['order_items_total'] = itemsTotal
            orderJson['order_shipping_method'] = shippingMethod
            ###orderJson['order_shipping_mail_class'] = shippingMailClass
            orderJson['order_date'] = orderDate
            orderJson['canadian_tax'] = canadianTax
            orderJson['vat_tax_paid'] = vat_tax_paid
            orderJson['display_canadian_tax'] = display_canadian_tax
            orderJson['display_euro_vat_tax'] = display_euro_vat_tax
            orderJson['display_uk_vat_tax'] = display_uk_vat_tax
            orderJson['display_canada_zero_rated_tax'] = display_canada_zero_rated_tax
            orderJson['vat_currency_code'] = vat_currency_code
            orderJson['platform'] = 'etsy'
            ###orderJson['private_notes'] = privateNotes
            
            total_item_quantity = 0
            
            customOrder = False
            #print('customOrder1', customOrder)
            defaultOrderedWithPersonalization = False
            personalizedOrderedWithNoInstructions = False

            for products in result['transactions']:
                productOrdered = products['title']
                productQuantity = products['quantity']
                total_item_quantity += productQuantity
                variation = products['variations']
                if (len(variation) == 0):
                    productType = ''
                    personalization = ''
                else:
                    try:
                        productType = variation[0]['formatted_value']
                    except:
                        productType = ''
                    try:
                        personalization = variation[1]['formatted_value']
                    except:
                        personalization = ''
                if ('default' in productType.lower() and personalization != 'Not requested on this item.'):
                    defaultOrderedWithPersonalization = True
                if ('message' in productType.lower()):
                    customOrder = True
                    #print('customOrder2', customOrder)
                    if (buyerNotes == '' and personalization == ''):
                        personalizedOrderedWithNoInstructions = True
                    if (buyerNotes == '' and personalization == 'Not requested on this item.'):
                        personalizedOrderedWithNoInstructions = True
                #personalization = cleanUpTextForRecieptPrinter(personalization)
                orderJson['products'].append({'product_name': productOrdered, 'product_quantity': productQuantity, 'product_type': productType, 'personalization': personalization})
            


            orderJson['is_custom_order'] = customOrder
            orderJson['default_ordered_with_personalization'] = defaultOrderedWithPersonalization
            orderJson['personalized_ordered_with_no_instructions'] = personalizedOrderedWithNoInstructions
            
            
            #shippingInfo = orderDetails['fulfillment']
            
                
            orderJson['recipient_name'] = result['name']    
            
            #if (buyerName == ''):
            #    orderJson['buyer_name'] = shippingInfo['to_address']['name']
            
            orderJson['buyer_phone'] = "" #shippingInfo['to_address']['phone']      NEED TO UPDATE THIS
            orderJson['buyer_address1'] = result['first_line']
            orderJson['buyer_address2'] = result['second_line']
            if (orderJson['buyer_address2'] == None):
                orderJson['buyer_address2'] = ''
                
            orderJson['buyer_address3'] = ''
            orderJson['buyer_city'] = result['city']
            orderJson['buyer_state_province'] = result['state']
            orderJson['buyer_postal_code'] = result['zip']
            #orderJson['buyer_country'] = result['country']
            
            #countryCode = countryCodeList[countryNameList.index(shippingInfo['to_address']['country'])]
            countryCode = result['country_iso']
            orderJson['buyer_country'] = countryNameList[countryCodeList.index(result['country_iso'])]
            
            if (countryCode == 'US'):
                orderJson['is_international'] = False
            else:
                orderJson['is_international'] = True
                
            orderJson['buyer_company'] = ''
            orderJson['buyer_country_code'] = countryCode
            orderJson['total_item_quantity'] = total_item_quantity

            
            if (result['is_shipped'] == False):  #only ship if not shipped
                pass

            #loopIndex += 1
            
            #orderJson = json.dumps(orderJson)
            
            
            #############
            #orderDetails = getOrderInfo(orderID)
                    
            #orderDetails = json.loads(orderDetails)
            
            jsonFileName = f"etsy_orderDetails-{orderJson['order_id']}.json"
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
            
            newOrderDate = orderJson['order_date']#.strip()
            newOrderDate = datetime.strptime(newOrderDate, '%B %d, %Y')
            newOrderDate = newOrderDate.strftime('%m/%d/%Y')
            
            orderJson['order_date'] = newOrderDate
            
            newOrderState = 'New'
                
            orderJson['order_state'] = newOrderState
            
            
            for i in range(numberOfProducts):
                #print('i', i)
                #flattenedDetails = ''
                flattenedDetails = {**orderJson}
                orderNumber = flattenedDetails['order_id']
                if (numberOfProducts > 1):
                    flattenedDetails['order_id'] = f"{orderNumber}-MULTI-{i+1}"
                    #print('flattenedDetails--', i , flattenedDetails['order_id'])
                #print('##############################')
                #print('flattenedDetails1', flattenedDetails, i)
                #print('##############################')
                singleProduct = orderJson['products'][i]
                #print('singleProduct', singleProduct)
                #print('##############################')
                #flattenedDetails.update(singleProduct)
                dict3 = {**flattenedDetails, **singleProduct}
                #print('flattenedDetails2', flattenedDetails, i)
                #print('##############################')
                del dict3['products'] 
                etsyCombinedOrders.append(dict3)
                #print('flattenedDetails3', flattenedDetails, i)
                #print('##############################')

            
                #print('orderDetails ---- ', orderDetails)
                
                #input('continue?')

                #for entries in etsyCombinedOrders:
                #    del entries['products']
                    #print('entries', entries['products'])
                
                
            #print(etsyCombinedOrders)
            
            
            
            with open('etsy_orders_in_json.json', 'w') as file:
                #print('saving file...')
                json.dump(etsyCombinedOrders, file, indent=4)
        
    except Exception as e:
        print('Error: etsyGetJson')
        print(e)
        traceback.print_exc()
    #etsyCombinedOrders
    print('DONE')
    print('##################################################################')
    return(etsyCombinedOrders)
            
                
#######################################################################
