from logging import exception
import logging
import os
import platform
import random
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
    my_parser.add_argument('-i', '--imagefile', nargs='+', default=['image1.jpeg', 'image2.jpeg', 'image3.jpeg'], help='the image files to be sent')
    my_parser.add_argument('-d', '--chromedriver', default='chromedriver', help='the full path for chromedriver including directory')
   
    args = my_parser.parse_args()

    if os.path.exists(args.numbersfile) == False: 
        print ('Numbersfile does not exist')
        sys.exit(1)
    else:
        file_numbers=args.numbersfile
    
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

#
# function to see if an index exists for an array or not
#
def index_exists(ls, i):
    return (0 <= i < len(ls))

#
# function to sanitize whatsapp no so that we don't get invalid number error
#
def sanitize(numstring):
    newnumber=numstring.replace("(", "")
    newnumber=newnumber.replace(")", "")
    newnumber=newnumber.replace("-", "")
    newnumber=newnumber.replace(" ", "")
    # if country code not given, default to +1 for US
    if len(newnumber)==10: newnumber="+1"+newnumber
    return newnumber

try:
    file = open(file_numbers, 'r')
    csv_reader = csv.reader(file)
    for row in csv_reader:
        sanitized_whatsapp_no = sanitize(row[0])
        whatsappnumber_from_csv.append(sanitized_whatsapp_no)
except:
    print("The numbers csv file input is invalid")
    exit(1)

file.close()

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
        print ('Sending image(s) to ' + whatsappnumber_from_csv[i])
        #
        # Open whatsapp web window for the contact. You don't need to save this contact in the phone.
        #
        driver.get('https://web.whatsapp.com/send/?phone=' + whatsappnumber_from_csv[i])
        #
        # only wait for the QR code authentication the first time, after that it will remember from cache
        # If the QR code authentication was done in the earlier session, even this is not needed, but it's necessary to have this step 
        # to make sure the authentication is successful
        #
        if i==0: input('\n\nPress enter after scanning QR code and put focus on Chrome window. DO NOT switch focus else sending will fail. You MUST WAIT till sending is done.')

        #
        # wait for the page to load, it can take a while sometimes
        #
        time.sleep(random.randint(10,15))

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
                time.sleep(1)

                #
                # click on image icon
                #
                image_box = driver.find_element(by=By.XPATH, value='//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
                image_box.send_keys(args.imagefile[j])
                time.sleep(2)

                #
                # click on send button
                #
                send_btn = driver.find_element(by=By.XPATH, value='//span[@data-icon="send"]')
                send_btn.click()
                time.sleep(5)

                print ('Image ' + args.imagefile[j] + ' sent successfully to ' + whatsappnumber_from_csv[i])
            except:
                #
                #  print the detailed error stack
                #
                logging.exception ('Could not send image ' + args.imagefile[j] + ' to ' + whatsappnumber_from_csv[i]); 
    except:
        #
        #  if the error file does not exist create it for the first time
        #
        if os.path.exists(errorfilename) == False: 
            errorfile = open(errorfilename, "w")
        
        #
        # construct an errormessage that replicates the current numbers.csv row 
        #`
        errormesg = whatsappnumber_from_csv[i] + '\n'
        
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
    errorfile.close()
driver.quit()