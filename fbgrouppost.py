import argparse
import csv
import logging
from operator import truediv
import os
import platform
import random
import re
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.action_chains import ActionChains

#
# parse arguments of the main program
#
try:
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('-u', '--username', required=True, help='the Facebook user name')
    my_parser.add_argument('-p', '--password', required=True, help='the Facebook password')
    my_parser.add_argument('-m', '--messagefile', default='fbmessage.txt', help='the file containing text message for facebook group posting')
    #my_parser.add_argument('-i', '--imagefile', default='fbimage.jpeg', help='the image file to be attached with facebook group posting')
    my_parser.add_argument('-g', '--groupsfile', default='fbgroups.txt', help='the file having URLs of Facebook groups')
    my_parser.add_argument('-d', '--chromedriver', default='chromedriver', help='the full path for chromedriver including directory')
   
    args = my_parser.parse_args()
    
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

    if os.path.exists(args.messagefile) == False: 
        print ('Messagefile does not exist')
        sys.exit(1)
    else:
        file_msg=args.messagefile

    if os.path.exists(args.groupsfile) == False: 
        print ('Groupsfile does not exist')
        sys.exit(1)
    else:
        file_groups=args.groupsfile

    #if os.path.exists(args.imagefile) == False: 
    #    print ('Imagefile does not exist')
    #    sys.exit(1)
    #else:
    #    file_image = pwd + delim + args.imagefile

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

print('Message file is ' + file_msg)
print('Groups file is ' + file_groups)
#print('Image file is ' + file_image)
print('Chromedriver file is ' + file_chromedriver)

#
# read the message into a variable 
#
with open(file_msg, 'r') as file:
   message = file.read()
print(message)

#
# read the groups and no of tabkeys to be pressed to reach Post field into arrays 
#
groups = []
#tabkeys = []
try:
    file = open(file_groups, 'r')
    csv_reader = csv.reader(file)
    for row in csv_reader:
        print('Now reading in group: ' + str(row))
        if (re.search("^#", row[0]) == None) and (len(row) > 0) :
            print('It is uncommented and is non empty')
            groups.append(row[0])
            # typecast into integer
            #tabkeys.append(int(row[1]))

    #print(len(groups), len(tabkeys))

except:
    print("The FB groups csv file input is invalid")
    file.close()
    exit(1)

##### Handling of Allow Pop Up In Facebook
option = Options()
option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
option.add_argument("--disable-extensions")

# Pass the argument 1 to allow and 2 to block
option.add_experimental_option("prefs", { 
    "profile.default_content_setting_values.notifications": 2 
})

driver = webdriver.Chrome(chrome_options=option, executable_path=file_chromedriver)
driver.maximize_window()
driver.get("https://www.facebook.com/")

###Login To The Account
def login(id,password):
    email = driver.find_element(by=By.XPATH, value="//input[@id='email']")
    email.send_keys(id)
    Password = driver.find_element(by=By.XPATH, value="//input[@id='pass']")
    Password.send_keys(password)
    driver.find_element(by=By.XPATH, value="//button[@name='login']").click()

#### Post Content On FaceBook
#def post_content_group(groupurl, nof_tabkeys, post, delay):
def post_content_group(groupurl, post, delay):
    
    try:
        driver.get(groupurl)
        time.sleep(5) ## Wait for it to load
        
        actions= ActionChains(driver) ##Action Chains
        
        WebDriverWait(driver, 25).until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Write something...']"))).click()
        #postbox = driver.find_element(by=By.XPATH, value="//span[normalize-space()='Write something...']")
        #postbox.click()
        #input('press enter')

        #
        # reach the Write something input box aka Fort Knox
        #
        #actions.send_keys(Keys.TAB * nof_tabkeys)  ##Press TAB
        #actions.send_keys(Keys.ENTER) ##Press ENTER
        #actions.perform() 
        #
        # wait for the post diaglog box to load
        #
        time.sleep(5)

        #input('Press enter')
        
        #
        # If needed, type like a real human with random delays in between
        #
        if delay == True:
            for char in post:
                start = 0.1 #please edit the speed here
                stop = 0.6 #change this (the maximum value is 1 or 0.9)
                step = 0.3
                precision = 0.1
                f = 1 / precision
                n = random.randrange(start * f, stop * f, step * f) / f
                #time.sleep(n)
                print(char)
                actions.send_keys(char)
        else:
            actions.send_keys(post)
        
        #
        # wait for the image previews to load
        #
        time.sleep(10)
        #
        # press the post button
        #
        actions.send_keys(Keys.TAB * 9)  ### Press TAB 9 Times to reach POST button
        actions.send_keys(Keys.ENTER) ### Press ENTER to post the content on facebook
        actions.perform()  ## To perfrom all the operations in the action chains

        #print('Messaged posted successfully for ' + groupurl + ' with ' + str(nof_tabkeys) + ' tabkeys')
        print('Messaged posted successfully for ' + groupurl)

        time.sleep(15)
        return True

    except:
        #logging.exception ('Could not post message for ' + groupurl + ' with ' + str(nof_tabkeys) + ' tabkeys')
        logging.exception ('Could not post message for ' + groupurl)
        return False
#
# main program
#
login(args.username,args.password) 
time.sleep(random.randrange(5,20))	

for i in range(len(groups)):
    #post_content_group(groups[i], tabkeys[i], message, False)
    post_content_group(groups[i], message, False)
    time.sleep(random.randrange(10,20))

driver.close()