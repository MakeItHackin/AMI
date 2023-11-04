import requests
import json
from datetime import datetime, timedelta
import cups
import sys
import traceback
import time

import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

ship_engine_api_key_sandbox = os.getenv('ship_engine_api_key_sandbox')
ship_engine_api_key_prod = os.getenv('ship_engine_api_key_prod')
ship_engine_carrier_id_sandbox = os.getenv('ship_engine_carrier_id_sandbox')
ship_engine_warehouse_id_sandbox = os.getenv('ship_engine_warehouse_id_sandbox')
ship_engine_warehouse_id_prod = os.getenv('ship_engine_warehouse_id_prod')
ship_engine_carrier_id_prod = os.getenv('ship_engine_carrier_id_prod')
ship_engine_ship_from_name = os.getenv('ship_engine_ship_from_name')
ship_engine_ship_from_phone = os.getenv('ship_engine_ship_from_phone')
ship_engine_ship_from_address_line_1 = os.getenv('ship_engine_ship_from_address_line_1')
ship_engine_ship_from_city = os.getenv('ship_engine_ship_from_city')
ship_engine_ship_from_state = os.getenv('ship_engine_ship_from_state')
ship_engine_ship_from_zip = os.getenv('ship_engine_ship_from_zip')
ship_engine_ship_from_country_code = os.getenv('ship_engine_ship_from_country_code')
ship_environment_is_prod = os.getenv('ship_environment_is_prod')
shipping_label_branding = os.getenv('shipping_label_branding')

###############################################################################


if (ship_environment_is_prod.lower() == 'true'):
    ship_environment_is_prod = True
else:
    ship_environment_is_prod = False
    

if (ship_environment_is_prod == False):
    print('SHIPPING ENVIRONMENT IS TEST')
    shipengine_APIKEY = ship_engine_api_key_sandbox  #this is test
else:
    print('SHIPPING ENVIRONMENT IS PROD')
    shipengine_APIKEY = ship_engine_api_key_prod  #this is prod

if (ship_environment_is_prod == False):
    shipEngineWarehouseID = ship_engine_warehouse_id_sandbox  #this is test
    carrier_id = ship_engine_carrier_id_sandbox #this is test
else:
    shipEngineWarehouseID = ship_engine_warehouse_id_prod #this is prod
    carrier_id = ship_engine_carrier_id_prod #this is prod

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

maxShipmentsPerDay = 6

###############################################################################

if (windowsOSBoolean == True):
    folderPath = codePath +  "\\shippingLabels\\" 
    labelsPath = codePath +  "\\labels\\"
else:
    folderPath = codePath  + "/shippingLabels/" 
    labelsPath = codePath  + "/labels/"

##############################################################################

def getManifestCount(ship_date):
    shippingManifestFile = folderPath + ship_date + ".json"
    if not os.path.exists(shippingManifestFile):
        number_of_packages = 0
    else:
        with open(shippingManifestFile, "r") as f:
            manifestJSON = json.load(f)  
        number_of_packages = len(manifestJSON['orders'])
    return number_of_packages


def createManifest(manifest_date):
    print('========================================================')
    
    shippingManifestFile = folderPath + manifest_date + ".json"
    
    if not os.path.exists(shippingManifestFile):
        number_of_packages = 0
        print('THERE ARE NO PACKAGES TO SHIP ON ' + manifest_date, 'NUMBER OF PACKAGES: ' + str(number_of_packages))
    else:
        with open(shippingManifestFile, "r") as f:
            manifestJSON = json.load(f)  
            
        number_of_packages = len(manifestJSON['orders'])
        
        print('CREATING MANIFEST FOR ' + manifest_date, 'NUMBER OF PACKAGES: ' + str(number_of_packages))
        
        
        label_array = []
        
        for order in manifestJSON['orders']:
            label_array.append(order['label_id'])
    
        print('LABEL ARRAY: ' + str(label_array))
                
        url = "https://api.shipengine.com/v1/manifests"

        payload = json.dumps({
        "label_ids": label_array
        })
        headers = {
        'Host': 'api.shipengine.com',
        'API-Key': shipengine_APIKEY,
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.status_code)
        
        json_response = response.json()
        #print('##################################################################')
        #print(json_response)
        #print('##################################################################')
        pretty_json = json.dumps(json_response, indent=4)
        #print(pretty_json)
        
        if (response.status_code != 200):
            print('ERROR CREATING MANIFEST')
            return False
        else:
            print('MANIFEST CREATED SUCCESSFULLY')
            manifest_content = json_response
            
            manifest_id = manifest_content['manifest_id']
            form_id = manifest_content['form_id']
            #manifest_ship_date = manifest_content['ship_date']
            manifest_labels = manifest_content['label_ids']
            manifest_submission_id = manifest_content['submission_id']
            manifest_link = manifest_content['manifest_download']['href']
            
            manifestJSON['manifest_id'] = manifest_id
            manifestJSON['form_id'] = form_id
            #manifestJSON['ship_date'] = manifest_ship_date
            manifestJSON['label_ids'] = manifest_labels
            manifestJSON['submission_id'] = manifest_submission_id
            manifestJSON['manifest_link'] = manifest_link
            
            with open(shippingManifestFile, 'w') as file:
                #print('saving file...')
                json.dump(manifestJSON, file, indent=4)
            
            print('========================================================')
        
            print('Downloading Manifest File...')

            response = requests.get(manifest_link)

            filename = 'manifest_' + manifest_date + '_' + form_id + '.pdf'
            filePath = folderPath + filename


            with open(filePath, 'wb') as f:
                f.write(response.content)
            try:
                conn = cups.Connection()
                printer_name = 'Brother_MFC_8910DW'
                print_job = conn.printFile(printer_name, filePath, '', {})
                print_status = conn.getJobAttributes(print_job)['job-state']

                if (print_status == 5):
                    print('Document Printed!')
                else:
                    print('Document NOT Printed!, Status: ' + str(print_status))
            except Exception as e:
                print('ERROR PRINTING DOCUMENT', e)
                traceback.print_exc()
        
    print('DONE')
    print('========================================================')
    return(True)

###############################################################################

def convertShipPrettyDate(ship_date_pretty):
    
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    monday = today + timedelta(days=(7 - today.weekday()))
    

    ship_date_pretty_today = today.strftime('%B %d')
    ship_date_pretty_tomorrow = tomorrow.strftime('%B %d')
    ship_date_pretty_monday = monday.strftime('%B %d')

    
    month, day_str = ship_date_pretty_today.split()
    # Convert the two-digit day to an integer
    day = int(day_str) 
    # Determine the ordinal suffix for the day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    # Construct the final formatted string
    ship_date_pretty_today = f"{month} {day}{suffix}"


    month, day_str = ship_date_pretty_tomorrow.split()
    # Convert the two-digit day to an integer
    day = int(day_str) 
    # Determine the ordinal suffix for the day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    # Construct the final formatted string
    ship_date_pretty_tomorrow = f"{month} {day}{suffix}"  
    
      
    month, day_str = ship_date_pretty_monday.split()
    # Convert the two-digit day to an integer
    day = int(day_str) 
    # Determine the ordinal suffix for the day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    # Construct the final formatted string
    ship_date_pretty_monday = f"{month} {day}{suffix}"  
    
    if (ship_date_pretty == ship_date_pretty_today):
        ship_date_pretty = 'today'
    elif (ship_date_pretty == ship_date_pretty_tomorrow):
        ship_date_pretty = 'tomorrow'
    elif (ship_date_pretty == ship_date_pretty_monday):
        ship_date_pretty = 'on Monday'
    else:
        ship_date_pretty = 'on ' + ship_date_pretty
    
    return(ship_date_pretty)
    
###############################################################################


def shipPackage(orderDetails):
    print('========================================================')
    print('SHIP PACKAGE')
    ship_date_pretty= ''

    service_code = orderDetails['verified_service_code']
    buyerPhone = orderDetails['buyer_phone']
    buyerAddressLine1 = orderDetails['verified_address_line1']
    buyerAddressLine2 = orderDetails['verified_address_line2']
    buyerAddressLine3 = orderDetails['verified_address_line3']
    buyerCityLocality = orderDetails['verified_city_locality']
    buyerStateProvince = orderDetails['verified_state_province']
    buyerPostalCode = orderDetails['verified_postal_code']
    buyerCountryCode = orderDetails['verified_country_code']
    buyerCountryCode = buyerCountryCode.upper()
    
    notes_for_shipment = orderDetails['verified_notes_for_shipment']
    
    customsQuantity = orderDetails['total_item_quantity']
    if (customsQuantity == ''):
        print('****** CUSTOMS QUANTITY WAS BLANK, ENTER QUANTITY:')
        customsQuantity = 1
    is_international = orderDetails['is_international']
    
    is_insured = orderDetails['verified_insurance']

    buyerName = orderDetails['buyer_name']
    recipientName = orderDetails['verified_name'] 

    isGift = orderDetails['order_is_gift']
    itemsTotal = orderDetails['order_items_total']
    itemsTotal = itemsTotal[1:]
    itemsTotal = float(itemsTotal)

    platform = orderDetails['platform']
    orderID = orderDetails['order_id']

    shipFromCompany = ""
    shipFromName = ship_engine_ship_from_name
    shipFromPhone = ship_engine_ship_from_phone
    shipFromAddressLine1 = ship_engine_ship_from_address_line_1
    shipFromAddressLine2 = ""
    shipFromAddressLine3 = ""
    shipFromCityLocality = ship_engine_ship_from_city
    shipFromStateProvince = ship_engine_ship_from_state
    shipFromPostalCode = ship_engine_ship_from_zip
    shipFromCountry = ship_engine_ship_from_country_code

    packageWeight = orderDetails['verified_package_weight']
    packageWeightType = orderDetails['verified_package_weight_type']
    packageLength = orderDetails['verified_package_length']
    packageWidth = orderDetails['verified_package_width']
    packageHeight = orderDetails['verified_package_height']
    packageDimensionUnit = orderDetails['verified_package_dimension_unit']
    ship_date_override = orderDetails['verified_ship_date_override']

    if (isGift == True):
        reference1 = '.  ' + "A Very Special Gift for You!"
        reference2 = '.  ' + "From: " + buyerName
        reference3 = '.  ' + platform + ' ' + str(orderID)
    else:
        reference1 = '.  ' + platform + ' ' + str(orderID)
        reference2 = '.  ' + "Thank you for supporting small businesses!"
        reference3 = '.  ' + "Have a Nerdy Day!"

    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    monday = today + timedelta(days=(7 - today.weekday()))
    current_hour = today.hour
    
    if (ship_date_override == True):
        print("Ship Date Override ", orderDetails['verified_ship_date'])  
        ship_date = orderDetails['verified_ship_date']
        datetime_obj = datetime.strptime(ship_date, "%Y-%m-%d")
        ship_date_pretty = datetime_obj.strftime('%B %d')
        shippingToday = False
        shippingTomorrow = False
        shippingMonday = False
    else:
        print("Ship date not overriden", "trying to ship on", orderDetails['verified_ship_date'])  
        
        shippingToday = False
        shippingTomorrow = False
        shippingMonday = False

        if (orderDetails['verified_ship_date'] in str(today) and current_hour < 10 and today.weekday() < 5):
            print("It's before 10am on a weekday, so we're shipping today")
            ship_date = today.strftime("%Y-%m-%d")
            ship_date_pretty = today.strftime('%B %d')
            shippingToday = True
        else:
            print("It's after 10am on a weekday, or not a weekday, so not shipping today.")
            #monday = today + timedelta(days=(7 - today.weekday()))
            # Check if tomorrow is a weekday
            if tomorrow.weekday() < 5:  # Monday is 0, Friday is 4
                # If tomorrow is a weekday, print tomorrow's date
                ship_date = tomorrow.strftime("%Y-%m-%d")
                ship_date_pretty = tomorrow.strftime('%B %d')
                shippingTomorrow = True
            else:
                # If tomorrow is a weekend, print Monday's date
                ship_date = monday.strftime("%Y-%m-%d")
                ship_date_pretty = monday.strftime('%B %d')
                shippingMonday = True
    
    month, day_str = ship_date_pretty.split()
    # Convert the two-digit day to an integer
    day = int(day_str) 
    # Determine the ordinal suffix for the day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    # Construct the final formatted string
    ship_date_pretty = f"{month} {day}{suffix}"
    
    ship_date_pretty = convertShipPrettyDate(ship_date_pretty)
    
    print('ship_date', ship_date, ship_date_pretty)   
    
    shippingManifestFile = folderPath + ship_date + ".json"
    
    ###############################################################################

    if (is_insured == True):
        insuredTotalValue = orderDetails['verified_insured_total_value']
        #insuredTotalValue += 
        insurance_provider = 'shipsurance'
        print('Shipping Insured', insuredTotalValue, insurance_provider)
    else:
        insuredTotalValue = 0
        insurance_provider = 'none'
        print('Shipping Domestically', insuredTotalValue, insurance_provider)
        
    
    customsPrice = (itemsTotal / customsQuantity)
    
    if (ship_environment_is_prod == True):
        label_image_id = shipping_label_branding  #company LOGO.  change this to a config variable
    else:
        label_image_id = ""
        
    payload = json.dumps({
    "label_image_id": label_image_id,
    "label_layout": "4x6",
    "shipment": {
        "service_code": service_code,
        "customs": {
            "contents": "merchandise",
            "non_delivery": "return_to_sender",
            "customs_items": [
            {
                "quantity": customsQuantity,
                "value": {
                "currency": "usd",
                "amount": customsPrice #itemsTotal
            },
            "harmonized_tariff_code": "9504.50.00",
            "country_of_origin": "US",
            "description": "Development Boards PCB",
            "sku": "nerdydevboards",
            "sku_description": "Development Boards PCB"
                }
            ]
        },
        "ship_date": ship_date,
        "ship_to": {
        "name": recipientName,
        "phone": buyerPhone,
        "address_line1": buyerAddressLine1,
        "address_line2": buyerAddressLine2,
        "address_line3": buyerAddressLine3,
        "city_locality": buyerCityLocality,
        "state_province": buyerStateProvince,
        "postal_code": buyerPostalCode,
        "country_code": buyerCountryCode,
        #"address_residential_indicator": "yes"
        },
        "warehouse_id": shipEngineWarehouseID,
        "confirmation": "none",
        "insurance_provider": insurance_provider,
        "packages": [
        {
            "weight": {
            "value": packageWeight,
            "unit": packageWeightType
            },
            "insured_value": {
            "currency": "usd",
            "amount": insuredTotalValue
            },
            "dimensions": {
                "height": packageHeight,
                "width": packageWidth,
                "length": packageLength,
                "unit": packageDimensionUnit
            },
            "label_messages": {
                "reference1": reference1,
                "reference2": reference2,
                "reference3": reference3
            }
        }
        ]
    }
    })

    headers = {
    'Host': 'api.shipengine.com',
    'API-Key': shipengine_APIKEY,
    'Content-Type': 'application/json'
    }

    url = "https://api.shipengine.com/v1/labels"
    
    response = requests.request("POST", url, headers=headers, data=payload)

    json_response = response.json()
    #print('##################################################################')
    #print(json_response)
    #print('##################################################################')
    
    if (response.status_code != 200):
        pretty_json = json.dumps(json_response, indent=4)
        print(pretty_json)

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        labels_file = labelsPath + 'labels.json'
        
        labelID = json_response['label_id']
        label_box_size = str(json_response['packages'][0]['dimensions']['length']) + 'x' + str(json_response['packages'][0]['dimensions']['width']) + 'x' + str(json_response['packages'][0]['dimensions']['height'])
        label_carrier_code = json_response['carrier_code']
        label_carrier_id = json_response['carrier_id']
        label_service_code = json_response['service_code']
        label_package_code = json_response['package_code']
        label_tracking_number = json_response['tracking_number']
        label_download_href = json_response['label_download']['href']
        label_download_pdf = json_response['label_download']['pdf']
        label_download_png = json_response['label_download']['png']
        label_download_zpl = json_response['label_download']['zpl']
        label_status = json_response['status']
        label_shipment_id = json_response['shipment_id']
        label_ship_date = json_response['ship_date']
        label_creation_date = json_response['created_at']
        label_shipment_cost = json_response['shipment_cost']['amount']
        label_insurance_cost = json_response['insurance_cost']['amount']
        label_is_international = json_response['is_international']
        label_is_voided = json_response['voided']
        label_voided_date = json_response['voided_at']
        label_label_id = json_response['label_id']
        label_tracking_status = json_response['tracking_status']
        label_insurance_claim = json_response['insurance_claim']
        label_customer_email = orderDetails['buyer_email']
        label_customer_name = orderDetails['buyer_name']
        label_customs_quantity = customsQuantity
        label_customs_value = customsPrice
        label_is_insured = is_insured
        label_notes = notes_for_shipment
        label_order_notes = orderDetails['order_notes']
        label_order_date = orderDetails['order_date']
        label_order_id = orderDetails['order_id']
        label_order_payment_total = orderDetails['order_payment_total']
        label_order_platform = orderDetails['platform']
        label_order_private_notes = orderDetails['private_notes']
        label_recipient_name = orderDetails['verified_name']
        label_order_ship_by_date = orderDetails['ship_by_date']
        label_shipping_address = orderDetails['verified_address_line1'] + ' ' + orderDetails['verified_address_line2'] + ' ' + orderDetails['verified_address_line3'] + ' ' + orderDetails['verified_city_locality'] + ' ' + orderDetails['verified_state_province'] + ' ' + orderDetails['verified_postal_code'] + ' ' + orderDetails['verified_country_code']
        label_shipping_method = orderDetails['order_shipping_method']
        label_order_shipping_paid_by_customer = orderDetails['order_shipping_total']
        label_shipment_id = json_response['shipment_id']
        label_weight = packageWeight
        label_weight_unit = packageWeightType
        

        with open(labels_file, 'r') as label_json_file:
            # do something with the file
            label_data = json.load(label_json_file)
            label_data['date_time_updated'] = timestamp

            # Append a new dictionary to the 'labels' list in the 'label_data' dictionary
            label_data['labels'].insert(0, {  #label_data['labels'].append({
                'box_size': label_box_size,  # Set the 'box_size' key to the value of 'label_box_size'
                'carrier_code': label_carrier_code,  # Set the 'carrier_code' key to the value of 'label_carrier_code'
                'carrier_id': label_carrier_id,  # Set the 'carrier_id' key to the value of 'label_carrier_id
                'customer_email': label_customer_email,  # Set the 'customer_email' key to the value of 'label_customer_email'
                'customer_name': label_customer_name,  # Set the 'customer_name' key to the value of 'label_customer_name'
                'customs_quantity': label_customs_quantity,  # Set the 'customs_quantity' key to the value of 'label_customs_quantity'
                'customs_value': label_customs_value,  # Set the 'customs_value' key to the value of 'label_customs_value'
                'insurance_claim': label_insurance_claim,  # Set the 'insurance_claim' key to the value of 'label_insurance_claim'
                'insurance_cost': label_insurance_cost,  # Set the 'insurance_cost' key to the value of 'label_insurance_cost'
                'is_insured': label_is_insured,  # Set the 'is_insured' key to the value of 'label_is_insured'
                'is_international': label_is_international,  # Set the 'is_international' key to the value of 'label_is_international'
                'is_manifested': False,  # Set the 'is_manifested' key to the value of 'label_is_manifested'
                'is_voided': label_is_voided,  # Set the 'is_voided' key to the value of 'label_is_voided'
                'label_creation_date': label_creation_date,  # Set the 'creation_date' key to the value of 'label_creation_date'
                'label_download_href': label_download_href,  # Set the 'download_href' key to the value of 'label_download_href'
                'label_download_pdf': label_download_pdf,  # Set the 'download_pdf' key to the value of 'label_download_pdf'
                'label_download_png': label_download_png,  # Set the 'download_png' key to the value of 'label_download_png'
                'label_download_zpl': label_download_zpl,  # Set the 'download_zpl' key to the value of 'label_download_zpl'
                'label_id': label_label_id,  # Set the 'label_id' key to the value of 'label_label_id'
                'label_status': label_status,  # Set the 'status' key to the value of 'label_status'
                'manifest_id': '',  # Set the 'manifest_id' key to the value of 'label_manifest_id'
                'manifest_name': '',  # Set the 'manifest_name' key to the value of 'label_manifest_name'
                'notes': label_notes,  # Set the 'notes' key to the value of 'label_notes'
                'order_date': label_order_date,  # Set the 'order_date' key to the value of 'label_order_date'
                'order_id': label_order_id,  # Set the 'order_id' key to the value of 'label_order_id'
                'order_notes': label_order_notes,  # Set the 'order_notes' key to the value of 'label_order_notes'
                'order_payment_total': label_order_payment_total,  # Set the 'order_payment_total' key to the value of 'label_order_payment_total'
                'order_platform': label_order_platform,  # Set the 'order_platform' key to the value of 'label_order_platform'
                'order_private_notes': label_order_private_notes,  # Set the 'order_private_notes' key to the value of 'label_order_private_notes'
                'order_ship_by_date': label_order_ship_by_date,  # Set the 'order_ship_by_date' key to the value of 'label_order_ship_by_date'
                'order_shipping_paid_by_customer': label_order_shipping_paid_by_customer,  # Set the 'order_shipping_paid_by_customer' key to the value of 'label_order_shipping_paid_by_customer'
                'package_code': label_package_code,  # Set the 'package_code' key to the value of 'label_package_code'
                'recipient_name': label_recipient_name,  # Set the 'recipient_name' key to the value of 'label_recipient_name'
                'service_code': label_service_code,  # Set the 'service_code' key to the value of 'label_service_code'
                'shipment_cost': label_shipment_cost,  # Set the 'shipment_cost' key to the value of 'label_shipment_cost'
                'shipment_id': label_shipment_id,  # Set the 'shipment_id' key to the value of 'label_shipment_id'
                'ship_date': label_ship_date,  # Set the 'ship_date' key to the value of 'label_ship_date'
                'shipping_address': label_shipping_address,  # Set the 'shipping_address' key to the value of 'label_shipping_address'
                'shipping_method': label_shipping_method,  # Set the 'shipping_method' key to the value of 'label_shipping_method'
                'tracking_number': label_tracking_number,  # Set the 'tracking_number' key to the value of 'label_tracking_number'
                'tracking_status': label_tracking_status,  # Set the 'tracking_status' key to the value of 'label_tracking_status'
                'voided_at': label_voided_date,  # Set the 'voided_date' key to the value of 'label_voided_date'
                'weight': label_weight,  # Set the 'weight' key to the value of 'label_weight'
                'weight_unit': label_weight_unit,  # Set the 'weight_unit' key to the value of 'label_weight_unit'
                
            })

        
        # Open the same JSON file for writing
        with open(labels_file, 'w') as json_file:
            # Save the updated JSON data back to the file
            json.dump(label_data, json_file, indent=4)   
    except Exception as e:
        print('error 321', e)
        try:
            shippingError = json_response['errors'][0]['message'].upper()
        except Exception as e:
            shippingError = 'ERROR WHEN SHIPPING'
        return(json_response, response.status_code, ship_date_pretty, ship_environment_is_prod, shippingError)
    #print('123')    
    if (ship_environment_is_prod == True and response.status_code == 200):  # 
        #print('manifest block')
        if not os.path.exists(shippingManifestFile):
            print("Creating and adding to shipping manifest...")
            
            manifestTemplate = {
                "date": ship_date,
                "orders": [{
                "platform": platform,
                "order_id": orderID,
                "label_id": label_label_id,
                }]
            }
            
            with open(shippingManifestFile, 'w') as file:
            #print('saving file...')
                json.dump(manifestTemplate, file, indent=4)
            
        else:
            print("Reading Manifest...")
            with open(shippingManifestFile, "r") as f:
                manifestJSON = json.load(f)
                
            number_of_packages = len(manifestJSON['orders'])
            print('number_of_packages', number_of_packages)
            
            if (number_of_packages < maxShipmentsPerDay or ship_date_override == True):
                print("Adding to Manifest...")

                manifestJSON['orders'].append({
                    "platform": platform,
                    "order_id": orderID,
                    "label_id": labelID,
                })
                with open(shippingManifestFile, 'w') as file:
                    json.dump(manifestJSON, file, indent=4)
            else:
                print("Manifest is full for the day")
                print("Creating new manifest for next shipping day")
                
                if (shippingToday == True):
                    nextShippingDay = today + timedelta(days=1)
                elif(shippingTomorrow == True):
                    nextShippingDay = today + timedelta(days=2)
                elif(shippingMonday == True):
                    nextShippingDay = today + timedelta(days=(7 - today.weekday()))
                else:
                    nextShippingDay = orderDetails['verified_ship_date']
                    nextShippingDay = datetime.strptime(nextShippingDay, "%Y-%m-%d")
                    #dayAfterTomorrow = today + timedelta(days=2)

                # Check if tomorrow is a weekday
                if nextShippingDay.weekday() < 5:  # Monday is 0, Friday is 4
                    # If dayAfterTomorrow is a weekday, print dayAfterTomorrow's date
                    ship_date = nextShippingDay.strftime("%Y-%m-%d")
                else:
                    # If tomorrow is a weekend, print Monday's date
                    ship_date = monday.strftime("%Y-%m-%d")
                    
                shippingManifestFile = folderPath + ship_date + ".json"
                
                if not os.path.exists(shippingManifestFile):
                    print("Creating and adding to shipping manifest for day after tomorrow...")
                    #i = open(shippingManifestFile,'a')
                    #i.write(platform + '-' + str(orderID) + '#' + str(labelID) + '\n')
                    #print(lineToWrite)
                    #i.close()
                    manifestTemplate = {
                        "date": ship_date,
                        "orders": [{
                        "platform": platform,
                        "order_id": orderID,
                        "label_id": labelID,
                        }]
                    }
                    with open(shippingManifestFile, 'w') as file:
                    #print('saving file...')
                        json.dump(manifestTemplate, file, indent=4)
                else:
                    print("Reading Manifest...")
                    
                    with open(shippingManifestFile, "r") as f:
                        manifestJSON = json.load(f)
                    
                    number_of_packages = len(manifestJSON['orders'])
                    print('number_of_packages', number_of_packages)
                    
                    
            
                    if (number_of_packages > maxShipmentsPerDay - 1):
                        print('NEED TO GO TO POST OFFICE !!!')
                    print("Adding to Manifest...")

                    manifestJSON['orders'].append({
                        "platform": platform,
                        "order_id": orderID,
                        "label_id": labelID,
                    })
                    with open(shippingManifestFile, 'w') as file:
                        json.dump(manifestJSON, file, indent=4)
    else:
        print("Not in production, so not using shipping manifest")
    
    print('DONE')  
    print('========================================================')
      
    return(json_response, response.status_code, ship_date_pretty, ship_environment_is_prod, 'no error')


###############################################################################

def voidLabel(labelIDtoVoid):

    url = f"https://api.shipengine.com/v1/labels/{labelIDtoVoid}/void"

    payload={}
    headers = {
    'Host': 'api.shipengine.com',
    'API-Key': shipengine_APIKEY
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    json_response = response.json()

    return(response.status_code, json_response)

###############################################################################


def printLabel(platform, orderID, url):
    print('========================================================')
    filetype = url[len(url)-3:]
    
    print(f'Downloading {filetype.upper()} File...')

    response = requests.get(url)

    now = datetime.now()
    filename = platform + '_' + str(orderID) + f'_{now.strftime("%Y-%m-%d_%H-%M-%S")}.{filetype}'
    filePath = codePath + '/shippingLabels/'
    
    #print('filePath', filePath)

    with open(filePath + filename, 'wb') as f:
        f.write(response.content)
        
    if filetype == 'zpl':
        
        # Create a connection to the CUPS server
        conn = cups.Connection()

        printer_name = 'Zebra_ZM400'

        # Set the print options for the ZPL file
        print_options = {
            'media': '4x6',
            'fit-to-page': 'True',
            'raw': 'True',
        }

        # Submit the print job to the default printer
        print_job = conn.printFile(printer_name, filePath + filename, '', print_options)

    elif filetype == 'pdf':
        # Create a connection to the CUPS server
        conn = cups.Connection()

        printer_name = 'Zebra_ZM400'

        time.sleep(2)
        
        # Submit the print job to the default printer
        print_job = conn.printFile(printer_name, filePath + filename, '', {})

    time.sleep(2)
    # Check the status of the print job
    print_status = conn.getJobAttributes(print_job)['job-state']

    if (print_status == 5):
        print('Document Printed!')
    
    print('DONE')
    print('========================================================')
    return(response.status_code, print_status)

###############################################################################
###############################################################################

def getShippingRates(addressJSON):            
    #print(addressJSON, type(addressJSON))
    addressJSON = json.loads(addressJSON)
    url = "https://api.shipengine.com/v1/rates"

    recipientName = addressJSON['name']
    buyerAddressLine1 = addressJSON['address_line1']
    buyerAddressLine2 = addressJSON['address_line2']
    buyerAddressLine3 = addressJSON['address_line3']
    buyerCityLocality = addressJSON['city_locality']
    buyerStateProvince = addressJSON['state_province']
    buyerPostalCode = addressJSON['postal_code']
    buyerCountryCode = addressJSON['country_code']
    ship_date = addressJSON['ship_date']
    packageWeight = addressJSON['package_weight']
    packageWeightType = addressJSON['package_weight_type']
    insuredTotalValue = addressJSON['insured_total_value']
    packageHeight = addressJSON['package_height']
    packageWidth = addressJSON['package_width']
    packageLength = addressJSON['package_length']
    packageDimensionUnit = addressJSON['package_dimension_unit']
    customsQuantity = addressJSON['item_quantity']
    itemsTotal = insuredTotalValue

    customsPrice = (itemsTotal / customsQuantity)
    
    payload = json.dumps({
    "rate_options": {
        "carrier_ids": [
        carrier_id
        ]
    },
    "shipment": {
        "validate_address": "validate_and_clean",
        "ship_to": {
        "name": recipientName,
        "phone": "",
        "address_line1": buyerAddressLine1,
        "address_line2": buyerAddressLine2,
        "address_line3": buyerAddressLine3,
        "city_locality": buyerCityLocality,
        "state_province": buyerStateProvince,
        "postal_code": buyerPostalCode,
        "country_code": buyerCountryCode
        },
        "ship_date": ship_date,
        "warehouse_id": shipEngineWarehouseID,
        "packages": [
            {
                "weight": {
                "value": packageWeight,
                "unit": packageWeightType
                },
                "insured_value": {
                "currency": "usd",
                "amount": insuredTotalValue
                },
                "dimensions": {
                    "height": packageHeight,
                    "width": packageWidth,
                    "length": packageLength,
                    "unit": packageDimensionUnit
                }
            }
        ],
        "customs": {
            "contents": "merchandise",
            "non_delivery": "return_to_sender",
            "customs_items": [
            {
                "quantity": customsQuantity,
                "value": {
                "currency": "usd",
                "amount": customsPrice #itemsTotal
            },
            "harmonized_tariff_code": "9504.50.00",
            "country_of_origin": "US",
            "description": "Development Boards PCB",
            "sku": "nerdydevboards",
            "sku_description": "Development Boards PCB"
                }
            ]
        },
    }
    })
    headers = {
    'Host': 'api.shipengine.com',
    'API-Key': shipengine_APIKEY,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)


    json_response = response.json()


    try:
        responseRates = json_response['rate_response']['rates']
        # = []
        rateArray = [] #[('Select a Rate',)]
        packagesToExclude = ["medium_flat_rate_box", "large_flat_rate_box", "flat_rate_envelope", "letter", "flat_rate_padded_envelope", "flat_rate_legal_envelope"]
        #servicesToExclude = ["usps_media_mail", "usps_parcel_select"]
        servicesToExclude = ["usps_parcel_select"]
        rateText = ''
        
        updatedAddress = json_response['ship_to']

        rateJSON = {
            "ground_advantage_price": None,
            "first_class_price": None,
            "priority_mail_price": None,
            "priority_mail_small_box_price": None,
            "priority_mail_express_price": None,
            "first_class_international_price": None,
            "priority_mail_international_price": None,
            "priority_mail_express_international_price": None,
            "media_mail_price": None
        }
        
        for rate in responseRates:
            if (rate['service_code'] not in servicesToExclude and rate['package_type'] not in packagesToExclude):
                #print(rate['service_type'], rate['service_code'], rate['package_type'], rate['shipping_amount']['amount'])
                raw_value = rate['service_type'] + '-' + rate['service_code'] + '-' + rate['package_type'] + '-' + str(rate['shipping_amount']['amount'])
                rateText = raw_value + '\n' + rateText
                if (rate['service_code'] == 'usps_first_class_mail'):
                    rateJSON['first_class_price'] = rate['shipping_amount']['amount']
                elif (rate['service_code'] == 'usps_priority_mail' and rate['package_type'] == 'package'):
                    rateJSON['priority_mail_price'] = rate['shipping_amount']['amount']
                elif (rate['service_code'] == 'usps_priority_mail' and rate['package_type'] == 'small_flat_rate_box'):
                    rateJSON['priority_mail_small_box_price'] = rate['shipping_amount']['amount']
                elif (rate['service_code'] == 'usps_priority_mail_express'):
                    rateJSON['priority_mail_express_price'] = rate['shipping_amount']['amount']
                elif (rate['service_code'] == 'usps_first_class_mail_international'):
                    rateJSON['first_class_international_price'] = rate['shipping_amount']['amount']
                elif (rate['service_code'] == 'usps_priority_mail_international'):
                    rateJSON['priority_mail_international_price'] = rate['shipping_amount']['amount']
                elif (rate['service_code'] == 'usps_priority_mail_express_international'):
                    rateJSON['priority_mail_express_international_price'] = rate['shipping_amount']['amount']
                elif (rate['service_code'] == 'usps_media_mail'):
                    rateJSON['media_mail_price'] = rate['shipping_amount']['amount']
                elif (rate['service_code'] == 'usps_ground_advantage'):
                    rateJSON['ground_advantage_price'] = rate['shipping_amount']['amount']
                    
        #print('rateJSON--', rateJSON)    
        #print ('rateText', rateText)
        return(rateJSON, updatedAddress)
    except Exception as e:
        print('ERROR on getShippingRates', e)
        traceback.print_exc()
        return('ERROR on getShippingRates', json_response)

