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
from selenium.webdriver.common.action_chains import ActionChains

import time
import subprocess
import argparse
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_arguments():
    """Parse command-line arguments and provide usage example"""
    parser = argparse.ArgumentParser(description='Send WhatsApp messages with attachments.',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-n', '--numbersfile', default='numbers.csv', help='file containing WhatsApp numbers')
    parser.add_argument('-m', '--messagefile', default='message.txt', help='file containing text message')
    parser.add_argument('-a', '--attachments', nargs='*', default=[], help='attachment files to be sent (images, videos, etc.)')
    parser.add_argument('-w', '--wait', type=int, default=1, help='wait time in minutes for WhatsApp Web to load (default: 1)')
    parser.usage = parser.format_help()
    parser.usage += "\nExample usage:\n"
    parser.usage += " python script.py -n numbers.csv -m message.txt -a image1.jpg video1.mp4 -w 5\n"
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        print("\nRunning with default values...")
    return args

def prepare_attachment_paths(args):
    """Prepare absolute paths for attachment files"""
    OSname = platform.system()
    if OSname in ["Darwin", "Linux"]:
        pwd = subprocess.getoutput('pwd')
        delim = '/'
    elif OSname == "Windows":
        pwd = subprocess.getoutput('cd')
        delim = '\\'
    
    attachment_files = []
    for attachment in args.attachments:
        attachment_path = os.path.join(pwd, attachment)
        if not os.path.exists(attachment_path):
            logging.error(f'Attachment file {attachment_path} does not exist')
            sys.exit(1)
        attachment_files.append(attachment_path)
    return attachment_files

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

def send_message(driver, number, message, attachments, vars):
    """Send message and attachments to a WhatsApp number"""
    driver.get(f'https://web.whatsapp.com/send/?phone={number}')
    logging.info(f"Waiting for the page to load for '{number}'")

    #
    #  wait for sometime to load page
    #
    time.sleep(10)
    
    #input("Loaded contact page, PRESS ENTER to proceed")

    # 
    # Keep tabbing to reach message box
    #
    # try:
    #     # Press Tab to reach message box
    #     actions = ActionChains(driver)
    #     for _ in range(28):
    #         actions.send_keys(Keys.TAB).perform()
    #         time.sleep(0.3)
        
    #     #input("pressed tabs, PRESS ENTER to proceed")

    #     # Get the active element after tabbing
    #     # message_box = driver.switch_to.active_element
        
    #     logging.info(f"Tabbed to message box element for number {number}")

    # except Exception as e:
    #     logging.error(f"Failed to tab to message box element for number {number}: {str(e)}")
    #     return False

    #time.sleep(20)  # Additional wait after page load

    # Send the message first
    if message:
        try:
            new_message = message.replace("x1", vars['var1']).replace("x2", vars['var2']).replace("x3", vars['var3'])
            logging.info(f"Attempting to send message: {new_message}")

            message_lines_without_EOL = new_message.split('\n')

            # 
            # select all text based on platform
            # 
            actions = ActionChains(driver)
            if sys.platform == 'darwin':  # Mac
                actions.key_down(Keys.COMMAND).send_keys('a').key_up(Keys.COMMAND).perform()
            elif sys.platform.startswith('win'):  # Windows
                actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()   

            #
            #  type in the message
            #

            for aline in message_lines_without_EOL:
                actions = ActionChains(driver)
                actions.send_keys(aline)
                actions.key_down(Keys.SHIFT).send_keys(Keys.RETURN).key_up(Keys.SHIFT)
                time.sleep(0.02)
                actions.perform() 
            
            # for aline in message_lines_without_EOL:
            #     message_box.send_keys(aline)
            #     message_box.send_keys(Keys.SHIFT, '\n')
            # logging.info("Message entered in the text box")
            # time.sleep(10)

            #input("Typed in message, PRESS ENTER to proceed")

            actions.send_keys(Keys.RETURN).perform()

            # message_box.send_keys(Keys.ENTER)

            logging.info("Enter key pressed to send message")

            time.sleep(5)

        except Exception as e:
            logging.error(f"Failed to send text message to {number}: {str(e)}")
            return False


    # Then send attachments
    if attachments and attachments[0]:
        logging.info(f"Sending {len(attachments)} attachment(s) to {number}")
        for i, attachment in enumerate(attachments):
            if attachment:
                try:
                    attachment_box = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@title="Attach"]')))
                    logging.info(f"Attachment button found for number {number}")
                    attachment_box.click()
                    media_box = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')))
                    logging.info(f"Media input box found for number {number}")
                    media_box.send_keys(attachment)
                    send_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]')))
                    logging.info(f"Send button found for number {number}")
                    send_button.click()
                    logging.info(f'Attachment {i+1}/{len(attachments)} ({attachment}) sent successfully to {number}')
                    time.sleep(random.randrange(5, 10))
                except Exception as e:
                    logging.exception(f'Could not send attachment {i+1}/{len(attachments)} ({attachment}) to {number}: {str(e)}')
                    return False
    else:
        logging.info(f"No attachments specified for sending to {number}")

    return True

def main():
    args = parse_arguments()
    file_numbers, file_msg = validate_files(args)
    logging.info(f"Message file path: {os.path.abspath(file_msg)}")
    attachment_files = prepare_attachment_paths(args)
    data = read_csv_data(file_numbers)
    message = read_message(file_msg)
    logging.info(f"Message read from file (first 50 characters): {message[:50]}")
    driver = initialize_driver()
    
    logging.info(f"ATTENTION:")
    logging.info(f"Get your WhatsApp app ready. Open Settings->Linked Devices-> Enter passcode and open QR code scanner.. then press ENTER..")
    logging.info(f"TROUBLESHOOTING TIPS:")
    logging.info(f"After the QR scan, if the page load hangs after {args.wait} mins, just re-run the script, click LOGOFF on the chrome window, scan the QR code again.")
    logging.info(f"You can also clean the earlier WhatsApp cache with $rm -rf /tmp/whatsapp and re-run the script\n")
    input("PRESS ENTER to proceed")
    
    # Load WhatsApp Web and wait for the specified time
    driver.get('https://web.whatsapp.com/')
    logging.info(f"Waiting {args.wait} minutes for initial WhatsApp Web page to load... If this is too short for your account, increase it using the -w or --wait argument")
    
    time.sleep(args.wait * 60)  # Convert minutes to seconds
    

    error_filename = f"sendwhatsapp.py.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.err"
    sent_filename = f"sendwhatsapp.py.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sent"

    try:
        for i, number in enumerate(data['numbers']):
            try:
                logging.info(f'Sending message(s) to {number}: {i+1} of {len(data["numbers"])}')
                success = send_message(driver, number, message, attachment_files,
                                       {'var1': data['var1'][i], 'var2': data['var2'][i], 'var3': data['var3'][i]})
                if success:
                    with open(sent_filename, "a") as sent_file:
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        sent_file.write(f"{timestamp},{number},{data['var1'][i]},{data['var2'][i]},{data['var3'][i]}\n")
                else:
                    with open(error_filename, "a") as error_file:
                        error_file.write(f"{number},{data['var1'][i]},{data['var2'][i]},{data['var3'][i]}\n")
            except Exception as e:
                logging.exception(f'Could not send message to {number}: {str(e)}')
                with open(error_filename, "a") as error_file:
                    error_file.write(f"{number},{data['var1'][i]},{data['var2'][i]},{data['var3'][i]}\n")
    finally:
        driver.quit()

    if os.path.exists(error_filename):
        logging.info(f'\n\nSome messages could not be sent. Error file: {error_filename}')
    if os.path.exists(sent_filename):
        logging.info(f'\n\nSuccessfully sent messages are logged in: {sent_filename}')

if __name__ == "__main__":
    main()
