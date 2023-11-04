print('======================================================')
print('STARTING... ')


import json
import etsyGetJson as etsy
import tindieGetJson as tindie
import lectronzGetJson as lectronz
import shopifyGetJson as shopify

import os

import printReceipt
import platformFunctions
import shipEngineFunctions as shipEngine
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import math

import pygame.mixer

#########################################################################################################

load_dotenv()  # Load environment variables from .env file

is_raspberry_pi = os.getenv('is_raspberry_pi')

if (is_raspberry_pi.lower() == 'true'):
    is_raspberry_pi = True
else:
    is_raspberry_pi = False
    

if (is_raspberry_pi == True):
    #print('setting up GPIO')
    import RPi.GPIO as GPIO

    GPIO.setwarnings(False)
        # Set the GPIO mode to BCM
    GPIO.setmode(GPIO.BCM)

    LIGHT_RELAY_PIN = 18

    GPIO.setup(LIGHT_RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)

        
shopify_shipping_location_id = os.getenv('shopify_shipping_location_id')

print_receipt_event = False
print_shipping_label_event = False
light_show_event = False
siren_show_event = False

print_receipt_event = True
print_shipping_label_event = True
light_show_event = True
siren_show_event = True

combinedOrders = []
shippingEnvironmentIsProd = False


import pyttsx3
engine = pyttsx3.init()

voices = engine.getProperty('voices')       #getting details of current voice
rate = engine.getProperty('rate')   # getting details of current speaking rate

if (is_raspberry_pi == True):
    engine.setProperty('voice', voices[2].id)  #changing index, changes voices. o for male
    #print (rate)                        #printing current voice rate
    engine.setProperty('rate', 125)     # setting up new voice rate
else:
    engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female
    engine.setProperty('rate', 150)     # setting up new voice rate



"""VOLUME"""
volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
#print (volume)                          #printing current volume level
engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1

#########################################################################################################


def print_receipt(order_json):
    print('=======================================================================') 

    print('PRINTING RECEIPT')
    platform = order_json['platform']
    actualOrderID = order_json['order_id'].split('-')[0].strip()
    
    with open(f"{platform}_orderDetails-{actualOrderID}.json", 'r') as f:
        orderDetails = json.load(f)
        canadianTax = orderDetails['canadian_tax']
        vatTax = orderDetails['vat_tax_paid']
        vatCurrencyCode = orderDetails['vat_currency_code']
        display_canadian_tax = orderDetails['display_canadian_tax']
        display_euro_vat_tax = orderDetails['display_euro_vat_tax']
        display_uk_vat_tax = orderDetails['display_uk_vat_tax']
        display_canada_zero_rated_tax = orderDetails['display_canada_zero_rated_tax']
        
        try:
            if (printReceipt.printReceipt(orderDetails) == True):
                print('Receipt Printed')
            else:
                print('Error: Print Receipt Failed')
            #PRINT TAX SLIP
            if (display_canadian_tax == True):    
                print('Order has Canadian Tax, print a receipt with a message')
                if (printReceipt.printMessage(canadianTax + ' Provincial\nSales Tax Paid') == True):
                    print('Canadian Tax Slip Printed')
                else:
                    print('Error: Canadian Tax Slip Not Printed')
            elif (display_canada_zero_rated_tax == True):    
                print('Order has Canadian Tax, print a receipt with a message')
                if (printReceipt.printMessage('Contents have been rated for zero tax') == True):
                    print('Canadian Tax Slip Printed')
                else:
                    print('Error: Canadian Tax Slip Not Printed')
            elif (display_uk_vat_tax == True):
                print('Order has UK VAT Tax, print a receipt with a message')
                if (printReceipt.printMessage(vatCurrencyCode + ' ' + str(vatTax) + ' VAT Paid.\nEtsy UK VAT# 370 6004 28') == True):
                    print('UK VAT Tax Slip Printed')
                else:
                    print('Error: UK VAT Tax Slip Not Printed')
            elif (display_euro_vat_tax == True):
                print('Order has EURO VAT Tax, print a receipt with a message')
                if (printReceipt.printMessage(vatCurrencyCode + ' ' + str(vatTax) + ' VAT Paid.\nEtsy IOSS# IM3720000224,') == True):
                    print('EURO VAT Tax Slip Printed')
                else:
                    print('Error: EURO VAT Tax Slip Not Printed')
        except Exception as e:
            print('ERROR printing receipt', e)
    print('DONE')
    print('=======================================================================') 

    return

#########################################################################################################



def fulfill_order(order_json, trackingNumber, customerShipmentShipDate):
    print('=======================================================================') 
    print('FULFILLING ORDER')
    if (shippingEnvironmentIsProd == True):
        print('Shipping label was created in production environment.')

        
        actualOrderID = order_json['order_id'].split('-')[0].strip()
        platform = order_json['platform']
        buyerFirstName = order_json['buyer_name']
        buyerFirstName = buyerFirstName.split(' ')[0]
        buyerFirstName = buyerFirstName.capitalize()
        
        '''
        try:
            customerShipmentShipDate = st.session_state['ship_date_for_customer']
        except:
            customerShipmentShipDate = st.session_state['shippingDate'].strftime('%B %d')
        '''
            
        with open(f"{platform}_orderDetails-{actualOrderID}.json", 'r') as f:
            orderJson = json.load(f)
        
        if (platform == 'etsy'):
            is_buyer_repeat = order_json['buyer_is_repeat']
            
            trackingCompany = "usps"

            fulfillmentObject = platformFunctions.fulfillEtsyOrder(actualOrderID, trackingCompany, trackingNumber, customerShipmentShipDate)
            fulfillmentShipped = fulfillmentObject[0]
            fulfillmentStatus = fulfillmentObject[1]
            print('fulfillmentShipped', fulfillmentShipped)
            print('fulfillmentStatus', fulfillmentStatus)
            if (fulfillmentStatus == 'Completed'):
                print('Fulfillment was successful')
                try: 
                    if (platformFunctions.sendEmailToCustomer(orderJson, customerShipmentShipDate) == True):
                        print('Message Sent')
                    else:
                        print('Error: Message Not Sent')
                except Exception as e:
                    print('ERROR sending message', e)
            else:
                print('Fulfillment was not successful')
        elif (platform == 'tindie'):
            print('Fulling on Tindie')  
            trackingCompany = 'USPS'
            fulfillmentStatus = platformFunctions.fulfillTindieOrder(actualOrderID, trackingCompany, trackingNumber, customerShipmentShipDate)
            print('fulfillmentStatus', fulfillmentStatus)
            if (fulfillmentStatus == 200):
                print('Fulfillment was successful')
                try: 
                    if (platformFunctions.sendEmailToCustomer(orderJson, customerShipmentShipDate) == True):
                        print('Message Sent')
                    else:
                        print('Error: Message Not Sent')
                except Exception as e:
                    print('ERROR sending message', e)
            else:
                print('Fulfillment was not successful')

        elif (platform == 'mih'):
            print('Fulling on Shopify')
            
            locationID = shopify_shipping_location_id
            trackingCompany = "USPS"
            trackingURL = "https://tools.usps.com/go/TrackConfirmAction.action?tLabels=" + trackingNumber
            
            fulfillmentObject = platformFunctions.fulfillShopifyOrder(orderJson['shopify_order_id'], locationID, trackingCompany, trackingNumber, trackingURL)
            fulfillmentID = fulfillmentObject[0]
            fulfillmentStatus = fulfillmentObject[1]

            if (fulfillmentStatus == 'success'):
                print('Fulfillment was successful')
                try: 
                    if (platformFunctions.sendEmailToCustomer(orderJson, customerShipmentShipDate) == True):
                        print('Message Sent')
                    else:
                        print('Error: Message Not Sent')
                except Exception as e:
                    print('ERROR sending message', e)
            else:
                print('Fulfillment was not successful')    
        
        elif (platform == 'lectronz'):
            print('Fulling on Lectronz')
            fulfillmentStatus = platformFunctions.fulfillLectronzOrder(actualOrderID, trackingNumber)
            if (fulfillmentStatus[0] == 'fulfilled'):
                print('Fulfillment was successful')
                try: 
                    if (platformFunctions.sendEmailToCustomer(orderJson, customerShipmentShipDate) == True):
                        print('Message Sent')
                    else:
                        print('Error: Message Not Sent')
                except Exception as e:
                    print('ERROR sending message', e)
            else:
                print('Fulfillment was not successful')
        else:
            print('Platform not supported yet')

    else:
        print('Not fulfilling order due to Shipping label was created in test environment.')
    print('DONE')
    print('=======================================================================')                        
    return

#########################################################################################################
                
def ship_package(order_json):
    print('=======================================================================') 
    print('SHIPPING PACKAGE')
    platform = order_json['platform']
    actualOrderID = order_json['order_id'].split('-')[0].strip()
    package_type = "package"
    service_code = 'usps_ground_advantage'
    packageWeight = 8
    packageWeightType = "ounce"
    shippingDate = datetime.now().strftime("%Y-%m-%d")         
    packageLength = 7
    packageWidth = 4
    packageHeight = 2
    packageDimensionUnit = "inch"
    insuredTotalValue = 0

            
    insuredGrandTotal = insuredTotalValue + math.ceil(float(order_json['order_shipping_total'][1:]))
    
    name = order_json['recipient_name']
    addressLine1 = order_json['buyer_address1']
    addressLine2 = order_json['buyer_address2']
    addressLine3 = order_json['buyer_address3']
    city = order_json['buyer_city']
    state = order_json['buyer_state_province']
    postalCode = order_json['buyer_postal_code']
    countryCode = order_json['buyer_country_code']
    insurance = False
    itemQuantity = order_json['total_item_quantity']
    ship_date_override = True
    verified_address_JSON = {
        "verified_ship_date": str(shippingDate),
        "verified_package_weight": packageWeight,
        "verified_package_weight_type": packageWeightType,
        "verified_package_length": packageLength,
        "verified_package_width": packageWidth,
        "verified_package_height": packageHeight,
        "verified_package_dimension_unit": packageDimensionUnit,
        "verified_insured_total_value": insuredGrandTotal,
        "verified_name": name,
        "verified_address_line1": addressLine1,
        "verified_address_line2": addressLine2,
        "verified_address_line3": addressLine3,
        "verified_city_locality": city,
        "verified_state_province": state,
        "verified_postal_code": postalCode,
        "verified_country_code": countryCode,
        "verified_service_code": service_code,
        "verified_insurance": insurance,
        "verified_item_quantity": itemQuantity,
        "verified_package_type": package_type,
        "verified_platform": platform,
        "verified_order_id": actualOrderID,
        "verified_ship_date_override": ship_date_override,
        "verified_notes_for_shipment": "celebration"
    }
                
    with open(f"{platform}_orderDetails-{actualOrderID}.json", 'r') as f:
        originalJSON = json.load(f)
        newJSON = {**originalJSON, **verified_address_JSON}

    if (originalJSON['order_id'] == newJSON['order_id']):
        print('order id matches.  good to ship.')
        customerShipment = shipEngine.shipPackage(newJSON)
        shippingErrorMessage = customerShipment[4]
        shippingEnvironmentIsProd = customerShipment[3]
        customerShipmentShipDate = customerShipment[2]
        customerShipmentStatusCode = customerShipment[1]
        customerShipment = customerShipment[0]

        if (customerShipmentStatusCode != 200):
            print('ERROR CREATING SHIPPING LABEL. STATUS CODE', customerShipmentStatusCode, shippingErrorMessage)
        else:
            labelID = customerShipment['label_id']
            labelStatus = customerShipment['status']
            labelShipmentID = customerShipment['shipment_id']
            labelTrackingNumber = customerShipment['tracking_number']
            labelPDFUrl = customerShipment['label_download']['pdf']
            labelZPLUrl = customerShipment['label_download']['zpl']
            shipped_date = customerShipment['ship_date']

            #print('platform', platform)
            #print('actualOrderID', actualOrderID)
            #print('labelPDFUrl', labelPDFUrl)

                
            shipped_date = datetime.strptime(shipped_date, '%Y-%m-%dT%H:%M:%SZ')
            
            printShippingLabelBoolean = True
            try:
                if (printShippingLabelBoolean == True):
                    print('Printing Shipping Label...')
                    shippingData = shipEngine.printLabel(platform, actualOrderID, labelPDFUrl)  #comboOrderID
                    shippingDownloadStatusCode = shippingData[0]
                    shippingPrintStatus = shippingData[1]
                    
                    print(shippingDownloadStatusCode, shippingPrintStatus)
                else:
                    print('Not printing shipping label due to global boolean')
            except:
                print('error printing shipping label')
            
            time.sleep(2)
            print_receipt(order_json)
            time.sleep(1)
                
            if (shippingEnvironmentIsProd == True):
                print('Shipping label was created in production environment, fulfilling order...')
                print("i commented this out so that i don't accidentally fulfill an order")
            else:
                print('Not fulfilling order because shipping label was created in test environment.')
    else:
        print('order id does not match')
    print('DONE')
    print('=======================================================================') 
    return

#########################################################################################################
                            

def start_light_show():
    if (is_raspberry_pi == True):
        if (light_show_event == True):
            print('light show')
            # Turn on the relay
            GPIO.output(LIGHT_RELAY_PIN, GPIO.LOW)
    return

#########################################################################################################

def stop_light_show():
    if (is_raspberry_pi == True):
        if (light_show_event == True):
            print('light show stopped')
            # Turn off the relay
            GPIO.output(LIGHT_RELAY_PIN, GPIO.HIGH)
            GPIO.cleanup()
    return

#########################################################################################################

def stop_siren_show():
    if (siren_show_event == True):
        #engine.stop()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Check every 10 milliseconds

        pygame.mixer.music.stop()
        pygame.mixer.quit()
        
        print('siren show stopped')


    return

#########################################################################################################

def start_siren_show():
    
    if (siren_show_event == True):
        print('siren show')
        
        pygame.mixer.init()

        pygame.mixer.music.set_volume(0.5)  # Adjust the volume between 0.0 and 1.0

        #print(3)
                    
        try:
            
            wav_file_path = "./media/win_effect.mp3"
            # Load and play the WAV file
            pygame.mixer.music.load(wav_file_path)
            #print(5)
            pygame.mixer.music.play()

        finally:
            pass
    return


    
            
            
#########################################################################################################

def new_order_event(new_order_id):
    print('=======================================================================') 
    print('NEW ORDER EVENT!!!')
    print('order_id: ', new_order_id)
    
    for orders in combinedOrders:
        actualOrderID = orders['order_id'].split('-')[0].strip()
        if (new_order_id == actualOrderID):
            new_order_json = orders
            print('new_order_json: ', new_order_json)
            break

    engine.say("new order was received on " + new_order_json['platform'])
    engine.runAndWait()

    if (print_shipping_label_event == True):
        ship_package(new_order_json)
                
    print('DONE')    
    print('=======================================================================') 
    return


#########################################################################################################


with open("celebration_orders.json", "r") as f:
    previous_orders = json.load(f)
    previous_orders = previous_orders['orders']

try:
    newEtsyData = etsy.getNewOrders(False, 0, 0) #(True, 10, 0)
except:
    print('ERROR: etsy.getNewOrders()')
    newEtsyData = []
try:            
    newTindieData = tindie.getNewOrders()
except:
    print('ERROR: tindie.getNewOrders()')
    newTindieData = []
try:
    newLectronzData = lectronz.getNewOrders(1)
except:
    print('ERROR: lectronz.getNewOrders()')
    newLectronzData = []
try:
    newShopifyData = shopify.getNewOrders()
    #newShopifyData = []
except:
    print('ERROR: shopify.getNewOrders()')
    newShopifyData = []
            
combinedOrders = newEtsyData + newTindieData + newShopifyData + newLectronzData

all_orders =[]

for orders in combinedOrders:
    actualOrderID = orders['order_id'].split('-')[0].strip()
    platform = orders['platform']
    if platform == 'etsy':
        actualOrderID = 'E' + actualOrderID
    elif platform == 'tindie':
        actualOrderID = 'T' + actualOrderID
    elif platform == 'shopify':
        actualOrderID = 'S' + actualOrderID
    elif platform == 'lectronz':
        actualOrderID = 'L' + actualOrderID
    if actualOrderID not in all_orders:
        all_orders.append(actualOrderID)


combinedJSON = {'orders': previous_orders, 'date': ''}

event_occurred = False

for order in all_orders:
    if order not in previous_orders:
        combinedJSON['orders'].append(order)
        if (event_occurred == False):
            event_occurred = True
            start_light_show()
            start_siren_show()
        new_order_event(order[1:])

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
combinedJSON['date'] = timestamp
    
with open("celebration_orders.json", "w") as file:
    json.dump(combinedJSON, file, indent=4)
    
if (event_occurred == True):
    stop_siren_show()
    stop_light_show()

