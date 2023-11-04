
import sys
import os

from escpos.printer import Usb


windowsOSBoolean = True

script_path = os.path.abspath(__file__)
codePath = os.path.dirname(script_path)

if ('/home/pi/' in codePath):
    windowsOSBoolean = False
    #print(codePath, "this is the pi")
else:
    #print(codePath, "this is windows")
    pass


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
    updated_string = updated_string.replace('&lt;', "<")
    updated_string = updated_string.replace('&#39;', "\'")
    return(updated_string)



def printMessage(message):
    p = Usb(0x0fe6,0x811e)  #milestone p80a
    try:
        p.set(align='center', font='a', text_type='normal', width=2, height=1, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='center', font='a', width=2, height=1, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)
    p.text(message + '\n')
    p.cut()
    p.close()
    return(True)
    
    
    
def splitMessage(string):
    lines = string.split('\n')
    result = ''
    for line in lines:
        # Split the line into chunks of length 48
        chunks = [line[i:i+48] for i in range(0, len(line), 48)]
        # Join the chunks with newline characters
        result += '\n'.join(chunks) + '\n'
    # Remove the extra newline character at the end
    return result.rstrip()


def printReceipt(orderDetails):

    p = Usb(0x0fe6,0x811e)  #milestone p80a
        
    buyerName = orderDetails['buyer_name']
    buyerName = cleanUpTextForRecieptPrinter(buyerName)
    buyerNotes = orderDetails['order_notes']
    buyerNotes = cleanUpTextForRecieptPrinter(buyerNotes)
    isGift = orderDetails['order_is_gift']
    giftMessage = orderDetails['order_gift_message']
    if (giftMessage == ''):
        giftMessage = 'A gift for you — enjoy!\nFrom:\n' + buyerName
    giftMessage = cleanUpTextForRecieptPrinter(giftMessage)
    paymentTotal = orderDetails['order_payment_total']
    taxTotal = orderDetails['order_tax_total']
    shippingTotal = orderDetails['order_shipping_total']
    itemsTotal = orderDetails['order_items_total']
    shippingMethod = orderDetails['order_shipping_method']
    productsOrdered = orderDetails['products']
    shipByDate = orderDetails['ship_by_date']
    orderDate = orderDetails['order_date']
    platform = orderDetails['platform']
    orderID = str(orderDetails['order_id'])

    try:
        p.set(align='center', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='center', font='a', width=1, height=1, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)

    p.image(codePath + '/logo.png')


    try:
        p.set(align='center', font='a', text_type='normal', width=2, height=1, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='center', font='a', width=1, height=2, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)

    p.text("\n\n")
    p.text("Thank you so much for\nsupporting my small\nelectronics business!\n")


    try:
        p.set(align='left', font='a', text_type='normal', width=2, height=1, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='left', font='a', width=1, height=2, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)

    p.text("\n")
    if (platform =='etsy'):
        p.text("ETSY ORDER# " + orderID + "\n")
    elif (platform == 'tindie'):
        p.text("TINDIE ORDER# " + orderID + "\n")
    elif (platform == 'mih'):
        p.text("SHOPIFY ORDER# " + orderID + "\n")
    elif (platform == 'lectronz'):
        p.text("LECTRONZ ORDER# " + orderID + "\n")
        
    try:
        p.set(align='left', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='left', font='a', width=1, height=1, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)
    p.text('Date Ordered: ' + orderDate + '\n')

    try:
        p.set(align='left', font='a', text_type='normal', width=2, height=1, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='left', font='a', width=2, height=1, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)
    p.text("\n")
    p.text("PRODUCTS PURCHASED:\n")

    try:
        p.set(align='left', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='left', font='a', width=1, height=1, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)
    
    for product in productsOrdered:
        productName = product['product_name']
        productQuantity = product['product_quantity']
        itemOptions = product['product_type']

        try:
            productType = ''
            for option in itemOptions:
                if (productType == ''):
                    productType = option['name'] + ' - ' + option['choice'] 
                else:
                    productType = productType + '\n' + option['name'] + ' - ' + option['choice']
        except:
            productType = itemOptions

        personalization = product['personalization']
        personalization = cleanUpTextForRecieptPrinter(personalization)
        
        if (personalization == 'Not requested on this item.'):
            personalization = ''
            
        if (len(personalization) > 48):
            personalization = splitMessage(personalization)

        p.text(productName + "\n")
        if (productType != ''):
            p.text("Product Type: " + productType + "\n")
        if (personalization != ''):
            p.text("Personalization:\n" + personalization + "\n")

        p.text("Quantity: " + str(productQuantity) + "\n")
        p.text("\n")
    
    try:
        p.set(align='left', font='a', text_type='normal', width=2, height=1, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='left', font='a', width=2, height=1, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)
    p.text("CUSTOMER: \n")

    try:
        p.set(align='left', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='left', font='a', width=1, height=1, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)
    p.text(buyerName + '\n')

    if (buyerNotes != ''):
        try:
            p.set(align='left', font='a', text_type='normal', width=2, height=1, density=9, invert=False, smooth=False, flip=False)
        except:
            p.set(align='left', font='a', width=2, height=1, density=9, invert=False, smooth=False, flip=False)        
            p.line_spacing(spacing=None, divisor=180)
        p.text("\n")  
        if (platform == 'etsy'):
            p.text("NOTES:\n")
        elif (platform == 'tindie'):
            p.text("NOTES/PERSONALIZATION:\n")
        elif (platform == 'mih'):
            p.text("NOTES/PERSONALIZATION:\n")
        elif (platform == 'lectronz'):
            p.text("NOTES/PERSONALIZATION:\n")
        
        try:
            p.set(align='left', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False, flip=False)
        except:
            p.set(align='left', font='a', width=1, height=1, density=9, invert=False, smooth=False, flip=False)        
            p.line_spacing(spacing=None, divisor=180)
        if (len(buyerNotes) > 48):
            buyerNotes = splitMessage(buyerNotes)
        p.text(buyerNotes + "\n") 


    if ('Standard International' in shippingMethod):
        shippingMethod = 'Standard International'

    try:
        p.set(align='left', font='a', text_type='normal', width=2, height=1, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='left', font='a', width=1, height=1, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)
    p.text("\n") 
    p.text("SHIPPING: \n")  

    try:
        p.set(align='left', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='left', font='a', width=1, height=1, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)
    p.text(shippingMethod + "\n")
    p.text(shipByDate + "\n")

    if (isGift == True):
        try:
            p.set(align='left', font='a', text_type='normal', width=2, height=1, density=9, invert=False, smooth=False, flip=False)
        except:
            p.set(align='left', font='a', width=2, height=1, density=9, invert=False, smooth=False, flip=False)        
            p.line_spacing(spacing=None, divisor=180)
        p.text("\n") 
        p.text("GIFT MESSAGE: \n") 
        
        try:       
            p.set(align='left', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False, flip=False)
        except:
            p.set(align='left', font='a', width=1, height=1, density=9, invert=False, smooth=False, flip=False)        
            p.line_spacing(spacing=None, divisor=180)
        if (len(giftMessage) > 48):
            giftMessage = splitMessage(giftMessage)
        p.text(giftMessage + "\n")
    else:
        try:
            p.set(align='left', font='a', text_type='normal', width=2, height=1, density=9, invert=False, smooth=False, flip=False)
        except:
            p.set(align='left', font='a', width=2, height=1, density=9, invert=False, smooth=False, flip=False)        
            p.line_spacing(spacing=None, divisor=180)
        p.text("\n") 
        p.text("TRANSACTION: \n") 
        
        try:
            p.set(align='left', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False, flip=False)
        except:
            p.set(align='left', font='a', width=1, height=1, density=9, invert=False, smooth=False, flip=False)        
            p.line_spacing(spacing=None, divisor=180)
        p.text('Item total: ' + itemsTotal + "\n")
        p.text('Shipping: ' + shippingTotal + "\n")
        if (platform != 'tindie'):
            p.text('Tax: ' + taxTotal + "\n")
        p.text('Order total: ' + paymentTotal + "\n")
        if ('International' in shippingMethod):
            p.text('(Prices are shown in USD)\n')
            
        if (platform == 'lectronz'):
            p.text("Totals may appear slightly off due to EUR to USD conversion from Lectronz.\n")

    try:
        p.set(align='center', font='a', text_type='normal', width=2, height=2, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='center', font='a', width=1, height=1, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)
    p.text("\n")

    p.text("\n")   

    try:
        p.set(align='center', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False, flip=False)
    except:
        p.set(align='center', font='a', width=1, height=1, density=9, invert=False, smooth=False, flip=False)    
        p.line_spacing(spacing=None, divisor=180)

    if (platform == 'tindie'):
        p.text("If you have any questions or concerns,\nplease send a message through Tindie.\n")
    elif (platform == 'etsy'):
        p.text("If you have any questions or concerns,\nplease send a message through Etsy.\n")
    elif (platform == 'mih'):
        p.text("If you have any questions or concerns,\nplease send a message through the order page.\n")
    elif (platform == 'lectronz'):
        p.text("If you have any questions or concerns,\nplease send a message through Lectronz.\n")
    
    p.text("Have a Wonderful and Nerdy Day!\n")

    p.text("\n")

    p.text("\n")


    p.cut() 
    
    p.close()

    return(True)