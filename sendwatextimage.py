import logging
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

    print('\n')
    print("make sure you format the csv file if downloaded from Google sheets")
    print("dos2unix contacts.csv")
    print('awk -f fixcontacts.awk <numbers.csv>')
    print('\n')

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
    main()
