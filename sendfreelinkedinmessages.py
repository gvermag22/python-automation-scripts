
import sys
import argparse
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_driver():
    """Set up the Chrome WebDriver with options."""
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("prefs", { 
            "profile.default_content_setting_values.notifications": 2 
        })
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.maximize_window()
        return driver
    except Exception as e:
        logger.error(f"Error setting up WebDriver: {e}")
        raise

def login_to_linkedin(driver, username, password):
    """Log in to LinkedIn."""
    logger.info("Navigating to LinkedIn login page")
    driver.get("https://www.linkedin.com/login")
    
    try:
        logger.info("Entering login credentials")
        username_field = driver.find_element(By.XPATH, "//*[@id='username']")
        username_field.send_keys(username)
        
        password_field = driver.find_element(By.XPATH, "//*[@id='password']")
        password_field.send_keys(password)

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        time.sleep(30)  # Wait for login to complete
        logger.info("Successfully logged in to LinkedIn")
    except Exception as e:
        logger.error(f"Error logging in to LinkedIn: {e}")
        raise

def get_profile_links(driver, search_url, num_pages):
    """Get profile links from search results."""
    driver.get(search_url)
    time.sleep(5)
    logger.info(f"Navigated to search URL: {search_url}")
    
    profile_urls = []
    
    for page in range(num_pages):  # Process specified number of pages
        logger.info(f"Processing page {page + 1}")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.reusable-search__entity-result-list"))
            )
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            profile_cards = driver.find_elements(By.CSS_SELECTOR, "li.reusable-search__result-container")
            logger.info(f"Found {len(profile_cards)} profile cards on page {page + 1}")

            for card in profile_cards:
                try:
                    link_element = card.find_element(By.CSS_SELECTOR, "a.app-aware-link")
                    profile_url = link_element.get_attribute('href')
                    if profile_url and "/in/" in profile_url:
                        clean_url = re.match(r'(https://www\.linkedin\.com/in/[^/?]+)', profile_url)
                        if clean_url:
                            profile_urls.append(clean_url.group(1))
                        else:
                            logger.warning(f"Could not clean URL: {profile_url}")
                except Exception as e:
                    logger.warning(f"Could not find link in a profile card: {e}")

        except Exception as e:
            logger.error(f"Error processing page {page + 1}: {str(e)}")
            break
        
        if page < num_pages - 1:  # Don't try to go to next page on the last iteration
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next']"))
                )
                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                next_button.click()
                time.sleep(5)
                logger.info(f"Navigated to page {page + 2}")
            except Exception as e:
                logger.error(f"Error navigating to page {page + 2}: {str(e)}")
                break
    
    return profile_urls

def extract_first_name(driver):
    """Extract the first name from the profile."""
    try:
        name_element = driver.find_element(By.XPATH, '//h1[@class="text-heading-xlarge inline t-24 v-align-middle break-words"]')
        full_name = name_element.text.strip()
        first_name = full_name.split()[0]  # Assuming the first word is the first name
        logger.info(f"Extracted first name: {first_name}")
        return first_name
    except Exception as e:
        logger.error(f"Error extracting first name: {str(e)}")
        return ""

# Update the visit_profile function to use send_message
def visit_profile(driver, profile_url, subject, message):
    """Open a profile, find the free message and send it."""
    try:
        # Open a new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(profile_url)
        logger.info(f"Visited profile: {profile_url}")
        
        time.sleep(3)  # Wait for the page to load

        # Extract the first name from the profile
        first_name = extract_first_name(driver)

        try:
            # Find the element with the ID top-card-text-details-contact-info
            element = driver.find_element(By.XPATH, '//*[@id="top-card-text-details-contact-info"]')
            element.click()  # Click on the element to focus it

        except Exception as e:
            logger.error(f"Error finding contact info of {profile_url}: {str(e)}")

        # Press escape to close any popup that may have opened
        actions = ActionChains(driver)
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(0.1)

        # keep tabbing forward till you find message button
        max_attempts = 10  # Set the maximum number of attempts
        attempts = 0  # Initialize the counter

        while attempts < max_attempts:
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
            focused_element = driver.switch_to.active_element
            button_text = focused_element.text.strip().lower()
            
            if button_text == "message":
                logger.info("Message button found")
                # Open the message box
                actions.send_keys(Keys.RETURN).perform()
                break
            
            attempts += 1  # Increment the counter

        if attempts == max_attempts:
            logger.info("Message button not found after maximum attempts")
            # else:
            #     logger.info("Found: " + button_text)

        #
        #  wait for the message box to load
        #
        time.sleep(4)

        #
        #  move forward 8 times to come to "why?" field per the new interfacce
        #

        actions = ActionChains(driver)
        for _ in range(8):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)

        # convert the button label to lowercase
        focused_element = driver.switch_to.active_element
        button_text = focused_element.text.strip().lower()

        if button_text == "upgrade my plan":
            logger.info("Out of InMail messages credits")
            
        #
        # Check if the message is free. This is the only quick and dirty check.
        # this is applicable for Premium acconts
        #
        if button_text == "why?":

            logger.info("Yay! Free message")

            #
            #  go back to the subject line box
            #
            for _ in range(8):
                actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
                time.sleep(0.2)
                logger.info("Moved to the subject field")

            # 
            # select all text based on platform
            # 
            if sys.platform == 'darwin':  # Mac
                actions.key_down(Keys.COMMAND).send_keys('a').key_up(Keys.COMMAND).perform()
            elif sys.platform.startswith('win'):  # Windows
                actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()    

            #  Type in the subject character by character
            #
            logger.info("Typing in the subject")
            prefixed_subject = f"{first_name}, {subject}"
            for char in prefixed_subject:
                actions = ActionChains(driver)
                actions.send_keys(char)
                time.sleep(0.02)
                actions.perform() 

            #
            # move to email body field
            #
            actions.send_keys(Keys.TAB).perform()

            # 
            # select all text based on platform
            # 
            if sys.platform == 'darwin':  # Mac
                actions.key_down(Keys.COMMAND).send_keys('a').key_up(Keys.COMMAND).perform()
            elif sys.platform.startswith('win'):  # Windows
                actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()  

            #
            #  Type in the email body character by character
            #
            logger.info("Typing in the message")
            prefixed_message = f"{first_name}, {message}"
            for char in prefixed_message:
                actions = ActionChains(driver)
                actions.send_keys(char)
                time.sleep(0.02)
                actions.perform() 

            # move to send button
            #
            for _ in range(5):
                actions.send_keys(Keys.TAB).perform()
                time.sleep(0.1)

            #
            # hit send
            #
            actions.send_keys(Keys.RETURN).perform()
            logger.info("Message sent!")

        #
        #  hit escape to close the message box if it's open
        #
        actions.send_keys(Keys.ESCAPE).perform()

        #
        #  wait for sometime before opening the next profile
        #
        time.sleep(3)

        # Close the tab
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])

    except Exception as e:
        logger.error(f"Error processing profile {profile_url}: {str(e)}")

def extract_message_parts(file_path):
    subject = ""
    body = ""
    in_body = False

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.lower().startswith("subject:"):
                subject = line[8:].strip()  # Extract subject from the same line
            elif line.lower().startswith("body:"):
                body = line[5:].strip()  # Extract body from the same line
                in_body = True
            elif in_body:
                body += "\n" + line

    return subject, body

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Profile Visitor and Connection Sender")
    parser.add_argument("--username", required=True, help="LinkedIn username or email")
    parser.add_argument("--password", required=True, help="LinkedIn password")
    parser.add_argument("--messagefile", required=True, help="Path to the file containing the message template")
    parser.add_argument("--searchurlfile", required=True, help="Path to the file containing the search results URL")
    parser.add_argument("--pages", type=int, default=1, help="Number of search result pages to process")
    args = parser.parse_args()

    logger.info("Script started with provided arguments")

    driver = setup_driver()
    logger.info("WebDriver initialized")

    try:
        login_to_linkedin(driver, args.username, args.password)

        subject, message = extract_message_parts(args.messagefile)
        logger.info(f"Extracted subject: {subject}")
        logger.info(f"Extracted message: {message}")

        with open(args.searchurlfile, 'r') as file:
            search_urls = [line.strip() for line in file if line.strip() and not line.strip().startswith('#')]

        for search_url in search_urls:
            profile_urls = get_profile_links(driver, search_url, args.pages)
            logger.info(f"Found {len(profile_urls)} profile URLs for search URL: {search_url}")

            for profile_url in profile_urls:
                visit_profile(driver, profile_url, subject, message)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

    finally:
        logger.info("Closing the browser")
        driver.quit()

if __name__ == "__main__":
     main()
