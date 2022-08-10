

import argparse
import logging
from operator import truediv
import os
import platform
import random
import subprocess
import sys
import time
import urllib.request, re
from requests import NullHandler
from selenium.webdriver.common.by   import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
# pip3 install selenium-stealth
from selenium_stealth import stealth
# pip3 install undetected-chromedriver
import undetected_chromedriver.v2 as uc


my_parser = argparse.ArgumentParser()
my_parser.add_argument('-k', '--keywordsfile', default='youtubekeywords.txt', help='the file containing keyword combinations for finding youtube videos')
my_parser.add_argument('-c', '--commentsfile', default='youtubecomments.txt', help='the file containing comments to be posted for each video')
my_parser.add_argument('-v', '--videosfile', default='youtubevideos.txt', help='the file to write to with youtube video links for keyword combinations')
my_parser.add_argument('-o', '--overwritevideos', default='no', help='denote whether videosfile should be overwritten or not')
my_parser.add_argument('-s', '--nofscrolls', default=10, help='the number of page scrolls for scraping youtube videos for a keywords combination')
my_parser.add_argument('-d', '--chromedriver', default='chromedriver', help='the full path for chromedriver including directory')

args = my_parser.parse_args()

if os.path.exists(args.keywordsfile) == False: 
    print ('Keywordsfile does not exist')
    sys.exit(1)

if os.path.exists(args.commentsfile) == False: 
    print ('Commentsfile does not exist')
    sys.exit(1)

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
#
# construct the full path to chromedriver
#
file_chromedriver = pwd + delim + args.chromedriver + extension

if os.path.exists(file_chromedriver) == False: 
    print ('Chromedriver does not exist')
    sys.exit(1)

print('Keywords file is ' + args.keywordsfile)
print('Comments file is ' + args.commentsfile)
print('Videos file is ' + args.videosfile)
print('# of scrolls is ' + str(args.nofscrolls))
print('Chromedriver file is ' + file_chromedriver)

#
# check if string is blank
#
def isBlank (myString):
    return not (myString and myString.isspace())

#
# read in the keyword combinations
#
keywords = []
with open(args.keywordsfile) as file:
    for index, keys in enumerate(file):
        #
        #  process if not commented
        #
        if (re.search("^#", keys) == None) and isBlank(keys) != False:
            print("Not commented or empty,read in " + keys)
            keys = re.sub(r"[ ]+", "+", keys)
            keys = re.sub(r"\n", "", keys)
            keywords.append(keys)
print (keywords)

#
# read in the comments
#
comments = []
with open(args.commentsfile) as file:
    for index, comment in enumerate(file):
        #
        #  process if not commented
        #
        if (re.search("^#", comment) == None) and isBlank(comment) != False:
            print("Not commented or empty,read in " + comment)
            comments.append(comment)
print (comments)

#
#  prepare options
#
options = webdriver.ChromeOptions()
if OSname=="Darwin" or OSname=="Linux": # MacOS/Unix
    options.add_argument("user-data-dir=/tmp/youtube")
elif OSname=="Windows": #Windows
    options.add_argument("user-data-dir=" + os.environ['USERPROFILE'] + "\\AppData\\Local\\Google\\Chrome\\User Data") 
driver = webdriver.Chrome(executable_path= file_chromedriver, options=options)

#
# enable stealth mode 
#
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

#
# function to remove duplicates in a list
#
def remove_duplicates(x):
  return list(dict.fromkeys(x))

#
# write the list of videos for keywords in a file
#
def generate_videos_list():
    #
    # search youtube URLs for keyword combinations
    #
    max_scrolls=args.nofscrolls
    file = open(args.videosfile, 'w')

    for i in range(0,len(keywords)):

        search_url = "https://www.youtube.com/results?search_query=" + keywords[i]
        print (search_url)
        
        #
        # load the youtube search page and wait for it to load
        #
        driver.get(search_url)
        driver.maximize_window()
        #
        #  sleep random time
        #
        time.sleep(random.randrange(5,15))

        nof_scrolls = 0
        while True:
            #
            # find all video links and load into videos list
            #
            user_data = driver.find_elements_by_xpath('//*[@id="video-title"]')
            for k in user_data:
            
                video_url = k.get_attribute('href')

                if video_url != None:
                    print (nof_scrolls, video_url)
                    file.write(video_url + "\n")
            #
            # select an element on the page, say body
            #
            element = driver.find_element_by_tag_name('body')
            #
            # Press the down key 
            #
            element.send_keys(Keys.PAGE_DOWN)
            #
            # if max_scrolls are reached then break away from loop
            #
            nof_scrolls = nof_scrolls + 1
            if nof_scrolls > max_scrolls: 
                break
            #
            # wait for page to load
            #
            time.sleep(random.randrange(5,10))
    #
    #  close the videosfile
    #
    file.close()

#
# function to find an element and click
#
def scroll_till_you_find_and_click_element(element_xpath, maxscrolls):
    #
    #  keep scrolling below till you find the element 
    #
    nofscrolls=0
    while nofscrolls < maxscrolls:

        try:
            element = driver.find_element(by=By.XPATH, value=element_xpath)
            element.click()
            # 
            # come out of the loop if the element is found and clicked
            #
            return element, True

        except Exception:
            driver.execute_script("window.scrollTo(0, 360)")
            nofscrolls = nofscrolls + 1
            time.sleep(3)

    return None, False

#
# function to comment on videos
#
def comment_on_videos_list():
    #
    # load all video URLs into a list
    #
    videos = []
    with open(args.videosfile) as file:
        for index, video in enumerate(file):
            #
            #  process if not commented
            #
            if (re.search("^#", comment) == None) and isBlank(video) != False:
                print("Not commented or empty,read in " + video)
                videos.append(video)
    # 
    # remove duplicate videos
    #            
    videos = remove_duplicates(videos)
    print (videos)

    actions = ActionChains(driver) ##Action Chains

    for j in range(0,len(videos)):

        video_url= videos[j]
        print(video_url)
        
        #
        # The input element to insert a new comment is not initially loaded on the page.
        # To make this element loaded you need to scroll the page down.
        # Also, to make the actual input comment element to be interactable you first need to click another element.
        #
        driver.get(video_url)
        #
        #  put random delays to simulate human activity
        #
        time.sleep(random.randrange(20,60))

        # 
        # Login for the first video
        # For later postings, the cookies will self-authenticate
        #
        if j == 0:
            input('Click a few videos, scroll up/down, watch for sometime to simulate human behavior, and press enter after login to Youtube...')
            #
            # reload first video
            #
            driver.get(video_url)
            #
            #  put random delays to simulate human activity
            #
            time.sleep(random.randrange(7,15))

        # find element within 5 scroll downs
        elem, bool = scroll_till_you_find_and_click_element("//*[@id='placeholder-area']", 5)
        if bool == False:
            logging.exception("Could not find the first element on youtube video page")
        
        # find element within 5 scroll downs
        elem, bool = scroll_till_you_find_and_click_element("//div[@id='contenteditable-root'][@aria-label='Add a comment...']", 5) 
        if bool == False:
            logging.exception("Could not find comment box on youtube video page")
        else:
            #
            # post a comment, tab to the post button, and press it
            #
            random_comment = comments[random.randrange(0, len(comments))]
            print ("Now posting comment = " + random_comment)

            elem.send_keys(random_comment)
            time.sleep(random.randrange(3,5))

            #input('press enter')

            elem, bool = scroll_till_you_find_and_click_element("//ytd-button-renderer[@id='submit-button']//yt-formatted-string[@id='text']", 1)
            if bool == True:
                print ('Comment posted successfully for ' + video_url)
            else:
                print ('Comment NOT posted for ' + video_url)

            # actions.send_keys(Keys.TAB * 2)  ##Press TAB
            # actions.send_keys(Keys.ENTER) ##Press ENTER
            # actions.perform() 

            #
            #  put random delays to simulate human activity
            #
            time.sleep(random.randrange(10,20))

        #input("Press enter after verifying comment posting..")

#
#  run the main program
#
if __name__ == '__main__':

    #
    # save videos in videosfile if it doesn't exist or the overwrite flag is on
    #
    if os.path.exists(args.videosfile) == False or args.overwritevideos.upper() in ["YES", "Y"]: 
        generate_videos_list()
    else:
        print("\nThe videosfile already exists and you chose not to overwrite it\n")
   
    input("Press ENTER if you want to continue with posting comments now? If not, press Control-C to abort...")

    comment_on_videos_list()

    driver.quit()