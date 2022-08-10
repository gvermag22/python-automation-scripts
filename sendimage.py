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
from selenium.webdriver.common.by   import By
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
                    #
                    # split the message into individual lines while stripping out end of line character so that the message doesn't get broken into multiple messages
                    #
                    message_lines_without_EOL=new_message.split('\n')

                    #
                    # now send each line one at a time
                    #
                    for aline in message_lines_without_EOL:
                        msg_box.send_keys(aline)
                        #
                        # Type SHIFT ENTER to simulate a new EOL character in the web window without creating a new message
                        #
                        msg_box.send_keys(Keys.SHIFT,'\n')
                    #print ('after send keys message for individual lines')
                    
                    time.sleep(random.randrange(5,10))

                #
                # click on send button
                #
                send_btn = driver.find_element(by=By.XPATH, value='//span[@data-icon="send"]')
                send_btn.click()
                time.sleep(random.randrange(5,10))

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