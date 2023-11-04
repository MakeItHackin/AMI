
import os
import time
import subprocess
import traceback


import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

avrdude_path_windows = os.getenv('avrdude_path_windows')
bootloader_flash_path_windows = os.getenv('bootloader_flash_path_windows')
avr_programmer_path_windows = os.getenv('avr_programmer_path_windows')

avrdude_path_pi = os.getenv('avrdude_path_pi')
bootloader_flash_path_pi = os.getenv('bootloader_flash_path_pi')
avr_programmer_path_pi = os.getenv('avr_programmer_path_pi')

avrdude_config_path_win = os.getenv('avrdude_config_path_win')
avrdude_config_path_rpi = os.getenv('avrdude_config_path_rpi')
projects_folder_win = os.getenv('projects_folder_win')
projects_folder_rpi = os.getenv('projects_folder_rpi')

windowsOSBoolean = True
#codePath = str(sys.path[0])

script_path = os.path.abspath(__file__)
# Get the directory containing the script
codePath = os.path.dirname(script_path)

if ('/home/pi/' in codePath):
    windowsOSBoolean = False
    #print(codePath, "this is the pi")
else:
    #print(codePath, "this is windows")
    pass


if (windowsOSBoolean == True):
    avrdudePath = avrdude_path_windows
    bootloaderFlashPath = bootloader_flash_path_windows
    avrProgammerPath = avr_programmer_path_windows
    programmerComPort = "COM5"
    cardFolderSuffix = '\\code\\'
    subFolderPrefix = '\\'
    codePath = codePath + '\\'
    product_path_suffix = '\\code\\'
    projects_folder = projects_folder_win
    avrdude_config_path = avrdude_config_path_win
else:
    avrdudePath = avrdude_path_pi
    bootloaderFlashPath = bootloader_flash_path_pi
    avrProgammerPath = avr_programmer_path_pi
    programmerComPort = "/dev/ttyACM0"
    cardFolderSuffix = '/code/'
    subFolderPrefix = '/'
    codePath = codePath + '/'
    product_path_suffix = '/code/'
    projects_folder = projects_folder_rpi
    avrdude_config_path = avrdude_config_path_rpi


#########################################################################################

status = 'Status not set'


def upload_default_code(product_index, product_name):
    status = ''           

    product_folder_name = product_name.replace(' ', '')
            
    product_path = projects_folder + product_folder_name + product_path_suffix
    default_file = product_path + product_folder_name + '.ino.hex'
        
    #print('default_file', default_file)
    #print('product_index', product_index)
    flashSize = '0'
    if (product_index == 0): #example product 1
        flashSize = '2250' # this should be whatever your default code compiles to
    elif (product_index == 1): #example product 2
        flashSize = '2270' # this should be whatever your default code compiles to
    elif (product_index == 2): #example product 3
        flashSize = '2268' # this should be whatever your default code compiles to   
    
    print("============================================================")
    print(f"Uploading Default {product_name} Code...")
    print()
    
    microcontroller_type = "atmega328p" #"t85"
    microcontroller_type = "-p" + microcontroller_type
    
    programmer_type = "arduino" #"avrisp"
    programmer_type = "-c" + programmer_type
    
    baud_rate = "115200" #"19200"
    baud_rate = "-b" + baud_rate
    
    proc2 = subprocess.run([avrdudePath, avrdude_config_path, microcontroller_type, programmer_type, "-P" + programmerComPort, baud_rate, "-Uflash:w:" + default_file + ":i"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    if (proc2.stderr != None):
        print('POSSIBLE ERROR!!!!!')
        status = 'Possible Arduino Upload error'
    else:
        uploadOutput = proc2.stdout.decode("utf-8")
        print(uploadOutput)
        index = 0
        uploadOutputLines = uploadOutput.splitlines()
        print(uploadOutputLines)
        for line in uploadOutputLines:
            print(index, line)
            index+=1
        print(uploadOutputLines[23])

        print('flashSize: ' + flashSize)
        if (flashSize in uploadOutputLines[23]):
            print(f'{product_name} Code Uploaded!')
            status = 'Arduino Upload Success!'

        else:
            print('UPLOAD FAILED?')
            status = 'Arduino upload error'
            print(uploadOutput)

    print()
    
    print(f"Done Uploading {product_name} Default Code!")
    print("============================================================")
    
    return(status)


#########################################################################################

def upload(upload_configs):
    status = ''
    custom_arduino_file_name = ''
    product_name = upload_configs['product_name']
    product_index = upload_configs['product_index']
    is_product_custom = upload_configs['is_product_custom']
    product_option = upload_configs['product_option']
    variable_1 = upload_configs['variable_1']
    variable_2 = upload_configs['variable_2']
    variable_3 = upload_configs['variable_3']
    variable_4 = upload_configs['variable_4']
    variable_5 = upload_configs['variable_5']
    variable_6 = upload_configs['variable_6']
    
    try:
        if (is_product_custom == False):
            return(upload_default_code(product_index, product_name))
        else:    
            product_folder_name = product_name.replace(' ', '')
            
            product_path = projects_folder + product_folder_name + product_path_suffix
            product_sub_folder = subFolderPrefix + product_folder_name 
            product_arduinoTextFile = product_path + product_folder_name + '.txt' 
        
            print()
            print('####################################################')
            print('CREATING CUSTOM CODE FOR:', product_name)
            print('####################################################')
                

            print("============================================================")
            print("Creating Arduino Sketch...")

            custom_arduino_file_name = product_path + product_sub_folder + product_sub_folder + ".ino"
            customArduinoFile = open(product_path + product_sub_folder + product_sub_folder + ".ino","w")

            customCode = open(product_arduinoTextFile, 'r')
            content = customCode.read()
            customCode.close()

            customArduinoFile.write('char custom_variable_1[] = "' + variable_1 + '";' + '\n')
            customArduinoFile.write('char custom_variable_2[] = "' + variable_2 + '";' + '\n')
            customArduinoFile.write('char custom_variable_3[] = "' + variable_3 + '";' + '\n')
            customArduinoFile.write('char custom_variable_4[] = "' + variable_4 + '";' + '\n')
            customArduinoFile.write('char custom_variable_5[] = "' + variable_5 + '";' + '\n')
            customArduinoFile.write('char custom_variable_6[] = "' + variable_6 + '";' + '\n\n')
            
            customArduinoFile.write(content)
            customArduinoFile.close()

            print("============================================================")
            print("Compiling Custom Arduino Sketch...")

            microcontroller_setting = "-barduino:avr:uno" 

            proc = subprocess.run([avrProgammerPath, "compile", product_path + product_sub_folder, microcontroller_setting], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            if (proc.stderr != None):
                print('POSSIBLE ERROR!!!!!')
                print(proc.stderr)
                status = 'Compile error'
            else:
                print(proc.stdout.decode("utf-8"))     
                
            print("============================================================")
            print("Uploading Custom Arduino Sketch...")

            proc = subprocess.run([avrProgammerPath, "upload", product_path + product_sub_folder, "-p" + programmerComPort, microcontroller_setting], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            if (proc.stderr != None):
                print('POSSIBLE ERROR!!!!!')
                print(proc.stderr)
            else:
                print(proc.stdout.decode("utf-8"))
                print()
                print('UPLOAD SUCCESSFUL!')
                status = 'Arduino Upload Success!'

            print("============================================================")

    except Exception as e:
        print('ERROR UPLOADING CODE ' + str(e))
        traceback.print_exc()
        status = 'Error' + str(e)

    print("Done!")
    print("============================================================")
    print()
    
    return(status, custom_arduino_file_name)

#########################################################################################