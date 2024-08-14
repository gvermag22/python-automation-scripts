from logging import exception
import logging
import os
import platform
import random
import re
import sys
from tkinter import W
from selenium import webdriver
import csv
from seleniumimport logging
import os
import platform
import random
import re
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import subprocess
import argparse
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_arguments():
    """Parse command-line arguments and provide usage example"""
    parser = argparse.ArgumentParser(description='Send WhatsApp messages with images.', 
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-n', '--numbersfile', default='numbers.csv', help='file containing WhatsApp numbers')
    parser.add_argument('-m', '--messagefile', default='message.txt', help='file containing text message for first image')
    parser.add_argument('-i', '--imagefiles', nargs='+', default=['image1.jpeg'], help='image files to be sent')
    
    parser.usage = parser.format_help()
    parser.usage += "\nExample usage:\n"
    parser.usage += "  python script.py -n numbers.csv -m message.txt -i image1.jpg image2.jpg\n"
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        print("\nRunning with default values...")
    
    return args

def prepare_image_paths(args):
    """Prepare absolute paths for image files"""
    OSname = platform.system()
    if OSname in ["Darwin", "Linux"]:  # MacOS/Unix
        pwd = subprocess.getoutput('pwd')
        delim = '/'
    elif OSname == "Windows":
        pwd = subprocess.getoutput('cd')
        delim = '\\'

    image_files = []
    for img in args.imagefiles:
        img_path = os.path.join(pwd, img)
        if not os.path.exists(img_path):
            logging.error(f'Image file {img_path} does not exist')
            sys.exit(1)
        image_files.append(img_path)
    
    return image_files

def validate_files(args):
    """Validate existence of input files"""
    for file in [args.numbersfile, args.messagefile]:
        if not os.path.exists(file):
            logging.error(f'File {file} does not exist')
            sys.exit(1)
    return args.numbersfile, args.messagefile

def read_csv_data(file_numbers):
    """Read data from CSV file"""
    data = {'numbers': [], 'var1': [], 'var2': [], 'var3': []}
    try:
        with open(file_numbers, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if not row[0].startswith('#'):
                    data['numbers'].append(row[0])
                    data['var1'].append(row[1] if len(row) > 1 else '')
                    data['var2'].append(row[2] if len(row) > 2 else '')
                    data['var3'].append(row[3] if len(row) > 3 else '')
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        sys.exit(1)
    return data

def read_message(file_msg):
    """Read message from file"""
    try:
        with open(file_msg, 'r', encoding='utf-8') as file:
            content = file.read()
            if not content.strip():
                logging.warning(f"The message file '{file_msg}' appears to be empty or contains only whitespace.")
            else:
                logging.info(f"Successfully read {len(content)} characters from '{file_msg}'")
            return content
    except IOError as e:
        logging.error(f"Error reading message file '{file_msg}': {e}")
        return ""

def initialize_driver():
    """Initialize and configure WebDriver"""
    options = Options()
    if platform.system() in ["Darwin", "Linux"]:
        options.add_argument("user-data-dir=/tmp/whatsapp")
    elif platform.system() == "Windows":
        options.add_argument(f"user-data-dir={os.environ['USERPROFILE']}\\AppData\\Local\\Google\\Chrome\\User Data")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    time.sleep(2)
    return driver

def send_message(driver, number, message, images, vars):
    """Send message and images to a WhatsApp number"""
    driver.get(f'https://web.whatsapp.com/send/?phone={number}')
    wait = WebDriverWait(driver, 20)  # Increased timeout to 30 seconds

    try:
        message_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="textbox" and @data-tab="10" and @aria-placeholder="Type a message"]')))
        logging.info(f"Message input box found for number {number}")
    except Exception as e:
        logging.error(f"Message input box not found for number {number}: {str(e)}")
        raise

    time.sleep(10)  # Additional wait after page load

    # Send the message first
    if message:
        try:
            new_message = message.replace("x1", vars['var1']).replace("x2", vars['var2']).replace("x3", vars['var3'])
            logging.info(f"Attempting to send message: {new_message}")
            message_box.clear()

            #
            # split the message into individual lines while stripping out end of line character so that the message doesn't get broken into multiple messages
            #
            message_lines_without_EOL=new_message.split('\n')

            #
            # now send each line one at a time
            #
            for aline in message_lines_without_EOL:
                message_box.send_keys(aline)
                #
                # Type SHIFT ENTER to simulate a new EOL character in the web window without creating a new message
                #
                message_box.send_keys(Keys.SHIFT,'\n')
            #print ('after send keys message for individual lines')

            logging.info("Message entered in the text box")
            time.sleep(10)
            
            #
            #input("press enter to send text message")
            #
            
            message_box.send_keys(Keys.ENTER)
            logging.info("Enter key pressed to send message")
            time.sleep(5)
        except Exception as e:
            logging.error(f"Failed to send text message to {number}: {str(e)}")

    # Then send images
    for i, img in enumerate(images):
        try:
            attachment_box = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@title="Attach"]')))
            logging.info(f"Attachment button found for number {number}")
            attachment_box.click()
            
            image_box = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')))
            logging.info(f"Image input box found for number {number}")
            image_box.send_keys(img)
            
            send_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]')))
            logging.info(f"Send button found for number {number}")
            send_button.click()
            
            logging.info(f'Image {img} sent successfully to {number}')
            time.sleep(random.randrange(5, 10))
        except Exception as e:
            logging.exception(f'Could not send image {img} to {number}: {str(e)}')
            raise

def main():
    """Main function to orchestrate the WhatsApp messaging process"""
    args = parse_arguments()
    file_numbers, file_msg = validate_files(args)
    logging.info(f"Message file path: {os.path.abspath(file_msg)}")
    
    image_files = prepare_image_paths(args)
    
    data = read_csv_data(file_numbers)
    message = read_message(file_msg)
    logging.info(f"Message read from file (first 50 characters): {message[:50]}")
    
    driver = initialize_driver()
    error_filename = f"sendimage.py.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.err"
    
    try:
        for i, number in enumerate(data['numbers']):
            try:
                logging.info(f'Sending image(s) to {number}: {i+1} of {len(data["numbers"])}')
                if i == 0:
                    input("After scanning QR code, press Enter to continue...")

                send_message(driver, number, message, image_files, 
                             {'var1': data['var1'][i], 'var2': data['var2'][i], 'var3': data['var3'][i]})
            except Exception as e:
                logging.exception(f'Could not send message to {number}: {str(e)}')
                with open(error_filename, "a") as error_file:
                    error_file.write(f"{number},{data['var1'][i]},{data['var2'][i]},{data['var3'][i]}\n")
    finally:
        driver.quit()
        if os.path.exists(error_filename):
            logging.info(f'\n\nSome messages could not be sent. Error file: {error_filename}')

if __name__ == "__main__":
    main().webdriver.common.by   import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import subprocess
import argparse
import datetime; 

#
# parse arguments of the main program
#
try:
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('-n', '--numbersfile', default='numbers.csv', help='the file containing whatsapp numbers')
    my_parser.add_argument('-m', '--messagefile', help='the file containing text message for first image')
    my_parser.add_argument('-i', '--imagefile', nargs='+', default=['image1.jpeg', 'image2.jpeg', 'image3.jpeg'], help='the image files to be sent')
    my_parser.add_argument('-d', '--chromedriver', default='chromedriver', help='the full path for chromedriver including directory')
   
    args = my_parser.parse_args()

    if os.path.exists(args.numbersfile) == False: 
        print ('Numbersfile does not exist')
        sys.exit(1)
    else:
        file_numbers=args.numbersfile
    
    if os.path.exists(args.messagefile) == False: 
        print ('Messagefile does not exist')
        sys.exit(1)
    else:
        file_msg=args.messagefile
    #
    # get current directory per OS
    #
    OSname=platform.system()
    if OSname=="Darwin" or OSname=="Linux": # MacOS/Unix
        pwd=subprocess.getoutput('pwd')
        delim='/'
        extension=''
    elif OSname=="Windows":
        pwd=subprocess.getoutput('cd') 
        delim='\\'
        extension='.exe'

    for i in range(len(args.imagefile)):
        args.imagefile[i] = pwd + delim + args.imagefile[i]
        # print(args.imagefile[i])
        if os.path.exists(args.imagefile[i]) == False: 
            print ('Image file ' + args.imagefile[i] + ' does not exist')
            sys.exit(1)

    #
    # construct the full path to chromedriver
    #
    file_chromedriver = pwd + delim + args.chromedriver + extension
    if os.path.exists(file_chromedriver) == False: 
        print ('Chromedriver does not exist')
        sys.exit(1)

except:
    print('Error in argument parsing')
    sys.exit(1)

print('Numbers file is ' + file_numbers)
print('Image file is ' + str(args.imagefile))
print('Chromedriver file is ' + file_chromedriver)


#
# Read numbers and personalized token values into arrays
# This program assumes max of 3 tokens that will be substitited
# 
whatsappnumber_from_csv = []
var1_from_csv = []
var2_from_csv = []
var3_from_csv = []

#
# function to see if an index exists for an array or not
#
def index_exists(ls, i):
    return (0 <= i < len(ls))

try:
    file = open(file_numbers, 'r')
    csv_reader = csv.reader(file)
    for row in csv_reader:
        #
        # this assumes that the phone numbers are in +1XXXXXXXXXX format
        # and the numbersfile has been treated with fixcontacts.awk script
        # If the numbers are not in +1XXXXXXXXXX format, the script will not work
        #
        # Only process rows that are not commented with # character in beginning
        #
        print('read in ' + str(row))
        if (re.search("^#", row[0]) == None):
            print('It is uncommented')
            whatsappnumber_from_csv.append(row[0])

            if index_exists(row, 1): var1_from_csv.append(row[1]); print('added var1 ' + row[1])
            if index_exists(row, 2): var2_from_csv.append(row[2]); print('added var2 ' + row[2])
            if index_exists(row, 3): var3_from_csv.append(row[3]); print('added var3 ' + row[3])

except:
    print("The numbers csv file input is invalid")
    file.close()
    exit(1)
    
file.close()

print('After reading from numbers file')
print(whatsappnumber_from_csv)
print(var1_from_csv)
print(var2_from_csv)
print(var3_from_csv)

#
# read the message into a variable 
#
with open(file_msg, 'r') as file:
   message = file.read()
print(message)

#
# prepare whatsapp window
#
options = Options();
if OSname=="Darwin" or OSname=="Linux": # MacOS/Unix
    options.add_argument("user-data-dir=/tmp/whatsapp")
elif OSname=="Windows": #Windows
    options.add_argument("user-data-dir=" + os.environ['USERPROFILE'] + "\\AppData\\Local\\Google\\Chrome\\User Data") 

driver = webdriver.Chrome(executable_path= file_chromedriver, options=options)

# store current time
tstamp = str(datetime.datetime.now())
tstamp = tstamp.replace(' ','_')
#
# construct filename for storing execution errors
#
errorfilename="sendimage.py." + tstamp + ".err"

#
# Loop through each whatsapp number and substitute the variable values into the message tokens
#
for i in range(len(whatsappnumber_from_csv)):
    try:
        print ('Sending image(s) to ' + whatsappnumber_from_csv[i] + ': ' + str(i) + ' of ' + str(len(whatsappnumber_from_csv)))
        #
        # Open whatsapp web window for the contact. You don't need to save this contact in the phone.
        #
        driver.get('https://web.whatsapp.com/send/?phone=' + whatsappnumber_from_csv[i])
        #
        # only wait for the QR code authentication the first time, after that it will remember from cache
        # If the QR code authentication was done in the earlier session, even this is not needed, but it's necessary to have this step 
        # to make sure the authentication is successful
        #
        if i==0: 
            print('\nAfter scanning QR code, do the following:\n') 
            print('1. Ensure computer is plugged into power.')
            print('2. Ensure computer setting are not set to sleep after long period of inactivity')
            print('3. Press Enter')
            print('4. Immediately switch back focus to the python-controlled Chrome window')
            print('5. DO NOT switch focus else sending will fail. You MUST WAIT till sending is done.')
            input()

        #
        # wait for the page to load, it can take a while sometimes
        #
        time.sleep(random.randrange(10,20))

        #
        # Loop through the images specified to send
        #
        for j in range(len(args.imagefile)):
            try:
                #
                # click on attach icon
                #
                attachment_box = driver.find_element(by=By.XPATH, value='//div[@title="Attach"]') 
                attachment_box.click()
                time.sleep(random.randrange(5,10))

                #
                # click on image icon
                #
                image_box = driver.find_element(by=By.XPATH, value='//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
                image_box.send_keys(args.imagefile[j])
                time.sleep(random.randrange(5,10))

                #
                # For the first image, put in the message if it was passed as a file 
                #
                if (j == 0) and (message != ""):
                    
                    #
                    # substitute the personalized token values into the message template
                    #
                    if index_exists(var1_from_csv, i): new_message = message.replace("x1", var1_from_csv[i])
                    if index_exists(var2_from_csv, i): new_message = new_message.replace("x2", var2_from_csv[i])
                    if index_exists(var3_from_csv, i): new_message = new_message.replace("x3", var3_from_csv[i])    
                    print('After substitution ' + new_message)

                    msg_box = driver.find_element(by=By.XPATH, value='//div[@role="textbox"]')
                    
                    msg_box.send_keys(new_message)

                    time.sleep(random.randrange(5,10))

                #
                # click on send button
                #
                #send_btn = driver.find_element(by=By.XPATH, value='//span[@data-icon="send"]')
                #send_btn.click()
                #time.sleep(random.randrange(5,10))

                print ('Image ' + args.imagefile[j] + ' sent successfully to ' + whatsappnumber_from_csv[i])
            except:
                #
                #  print the detailed error stack
                #
                logging.exception ('Could not send image ' + args.imagefile[j] + ' to ' + whatsappnumber_from_csv[i]); 
                raise
    except:
        #
        #  if the error file does not exist create it for the first time
        #
        if os.path.exists(errorfilename) == False: 
            errorfile = open(errorfilename, "w")
        
        #
        # construct an errormessage that replicates the current numbers.csv row 
        #`
        errormesg = whatsappnumber_from_csv[i]
        if index_exists(var1_from_csv, i): errormesg = errormesg + ',' + var1_from_csv[i]
        if index_exists(var2_from_csv, i): errormesg = errormesg + ',' + var2_from_csv[i]
        if index_exists(var3_from_csv, i): errormesg = errormesg + ',' + var3_from_csv[i]
        errormesg = errormesg + '\n'
        
        #
        #  print the detailed error stack
        #
        logging.exception ('Could not send message to ' + errormesg); 
        #
        # You can rename the error file as <anyfile>.csv and re-run the program another time with -n <anyfile>.csv
        # Usually, you should expect some whatsapp numbers to not go through the first time
        # This way you can keep trying sending to the unsent numbers till you are left with 
        # numbers that are not registered with Whatsapp at all
        #
        errorfile.write(errormesg)

# 
# if error file exists, close it
#
if os.path.exists(errorfilename) == True:
    print('\n\nSome messages could not be sent. You should rename the error file and rerun the program with it:')
    print('wc -l ' + errorfilename)
    print('mv ' + errorfilename + ' ' + file_numbers + '.err')
    errorfile.close()
driver.quit()
