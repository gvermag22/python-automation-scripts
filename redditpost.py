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
from turtle import title
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip as pc
from selenium.webdriver.common.keys import Keys

#
# parse arguments of the main program
#
try:
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('-u', '--username', required=True, help='the Reddit user name')
    my_parser.add_argument('-p', '--password', required=True, help='the Reddit password')
    my_parser.add_argument('-t', '--titlefile', default='redditmessagetitle.txt', help='the file containing title for Reddit group posting')
    my_parser.add_argument('-m', '--messagefile', default='redditmessage.txt', help='the file containing message for Reddit group posting')
    my_parser.add_argument('-g', '--groupsfile', default='redditgroups.txt', help='the file having URLs of Reddit groups')
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

    if os.path.exists(args.titlefile) == False: 
        print ('Titlefile does not exist')
        sys.exit(1)
    else:
        file_title=args.titlefile

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
print('Title file is ' + file_title)
print('Groups file is ' + file_groups)
print('Chromedriver file is ' + file_chromedriver)

#
# read the title into a variable 
#
with open(file_title, 'r') as file:
   title = file.read()
print(title)

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
    print("The Reddit groups csv file input is invalid")
    file.close()
    exit(1)

##### Handling of Allow Pop Up In Reddit
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

###Login To The Account
def login(id,password):

    driver.get("https://www.Reddit.com/login")

    actions= ActionChains(driver) ##Action Chains

    actions.send_keys(Keys.TAB * 4)  ## Reach login box
    actions.send_keys(id)
    #actions.perform() 

    actions.send_keys(Keys.TAB)  ## reach password box
    actions.send_keys(password)
    #actions.perform() 

    actions.send_keys(Keys.TAB * 2)  ## reach login button
    actions.send_keys(Keys.ENTER) ##Press ENTER
    actions.perform() 

#### Post Content On Reddit
def post_content_group(groupurl, tagline, post):
    
    try:
        driver.get(groupurl)
        time.sleep(10) ## Wait for it to load
        
        #actions= ActionChains(driver) ##Action Chains
        #
        # reach the post box
        #
        box = driver.find_element(by=By.XPATH, value="//input[@placeholder='Create Post']")
        box.click()
        #actions.send_keys(Keys.TAB * nof_tabkeys)  ##Press TAB
        #actions.send_keys(Keys.ENTER) ##Press ENTER
        #actions.perform() 
        time.sleep(2)

        #
        # reach the Title box
        #
        box = driver.find_element(by=By.XPATH, value="//textarea[@placeholder='Title']")
        box.click()
        #actions.send_keys(Keys.TAB * 8)  ##Press TAB
        box.send_keys(tagline) ##Press ENTER
        #actions.perform() 
        time.sleep(2)
        #
        # reach the message box
        #
        box = driver.find_element(by=By.XPATH, value="//div[@role='textbox']")
        box.click()
        #actions.send_keys(Keys.TAB)  ##Press TAB
        #box.send_keys(Keys.CONTROL, 'v')  #Paste using Ctrl+V
        box.send_keys(post) ##Press ENTER
        #actions.perform() 
        time.sleep(2)
        
        #
        # reach the post box
        #
        box = driver.find_element(by=By.XPATH, value="//button[@role='button'][contains(text(), 'Post')]")
        box.click()

        #time.sleep(5)

        return True

    except:
        logging.exception ('Could not post message for ' + groupurl)
        return False
#
# main program
#
login(args.username,args.password) 
time.sleep(5)	

# copy message to clipboard
#pc.copy(message)

for i in range(len(groups)):
    print(groups[i])
    #print(tabkeys[i])
    post_content_group(groups[i], title, message)
    input('Please verify the posting is proper and press enter')
    time.sleep(5)

driver.close()