
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
        
        time.sleep(10)  # Wait for login to complete
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

def click_and_process_connect_button(driver, focused_element, message_template, first_name):
    """Click the Connect button."""
    try:
        # click on the connect button to bring up the dialog box
        focused_element.send_keys(Keys.RETURN)
        logger.info("Clicked Connect button")
        time.sleep(2)

        # input ("in click_and_process_connect_button: After clicking on Connect Button. Hit enter")

        actions = ActionChains(driver)
        # Press tab twice to focus on the Add a note button and press enter
        for _ in range(2):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.1)
        actions.send_keys(Keys.RETURN).perform()

        time.sleep(2)
        
        # input ("in click_and_process_connect_button: After clicking on Add Note Button. Hit enter")

        # # Press tab six times to focus on message box
        # for _ in range(6):
        #     actions.send_keys(Keys.TAB).perform()
        #     time.sleep(0.1)

        # Send the message
        send_message(driver, message_template, first_name)
    except Exception as e:
        logger.error(f"Error clicking Connect button: {str(e)}")
        return False

def click_and_process_more_button(driver, focused_element, message_template, first_name):
    """Click the Follow button."""
    try:
        
        actions = ActionChains(driver)
        #
        # Press tab until the focused element's text is "more"
        # This logic is needed because sometimes people have Request Services button as well
        #
        while True:
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.1)
            focused_element = driver.switch_to.active_element
            button_text = focused_element.text.strip().lower()
            if button_text == "more":
                logger.info("More button found")
                break

        # Press enter to open the "more" menu box
        actions.send_keys(Keys.RETURN).perform()
        time.sleep(0.2)

        #
        # Press tab three times to focus on the Connect or Unfollow option 
        # Then press enter to bring up the message dialog box
        #
        for _ in range(3):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)

        focused_element = driver.switch_to.active_element
        menu_option_text = focused_element.text.strip().lower()

        #
        # check if the menu option is connect 
        #
        if menu_option_text == "connect":

            logger.info("Connect menu option found")

            actions.send_keys(Keys.RETURN).perform()
            time.sleep(0.1)

            # input ("click_and_process_more_button: After clicking on Connect Button. Hit enter")

            # Press tab twice to focus on the Add a note button and press enter
            for _ in range(2):
                actions.send_keys(Keys.TAB).perform()
                time.sleep(0.1)
            actions.send_keys(Keys.RETURN).perform()
            logger.info("Opened message box")

            # input ("click_and_process_more_button: After clicking on Add Note. Hit enter")
            
            time.sleep(2)

            # Send the message
            send_message(driver, message_template, first_name)

        elif menu_option_text == "follow":
            #
            # follow the person
            #
            actions.send_keys(Keys.RETURN).perform()
            logger.info("Followed the person.")

        elif menu_option_text == "unfollow":
            logger.info("Already following. Skipping.")

    except Exception as e:
        logger.error(f"Error clicking Follow button: {str(e)}")
        return False
            
def send_message(driver, message_template, first_name):
    """Send a message."""
    try:
        # Type in the message character by character
 
        # input ("Before entering message. Hit enter")

        prefixed_message = f"{first_name}, {message_template}"
       
        logger.info(f"Typing in the message \n {first_name}, {message_template}")

        for char in prefixed_message:
            actions = ActionChains(driver)
            actions.send_keys(char)
            time.sleep(0.02)
            actions.perform()

        # input ("Entered message. Hit enter")

        # Press tab few times to focus on send button 
        for _ in range(3):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.1)

        # send the message by pressing enter
        actions.send_keys(Keys.RETURN).perform()

        time.sleep(2)

        logger.info("Message sent successfully")

    except Exception as e:
        
        logger.error(f"Error sending message: {str(e)}")

# Update the visit_profile function to use send_message
def visit_profile(driver, profile_url, message_template):
    """Open a profile, find the connect button, add a note, and send a connection request."""
    try:
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

        # Press tab twice to focus on the message/connect/follow button
        actions = ActionChains(driver)
        for _ in range(2):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.1)

        # convert the button label to lowercase
        focused_element = driver.switch_to.active_element
        button_text = focused_element.text.strip().lower()

        # Check if the focused element is the Connect button
        if button_text == "connect":
            logger.info("Connect button found")
            click_and_process_connect_button(driver, focused_element, message_template, first_name)

        # Check if the focused element is the Follow button
        elif button_text == "follow":
            logger.info("Follow button found")

            # Press enter to click the Follow button
            actions.send_keys(Keys.RETURN).perform()
            logger.info("Followed contact successfully")
            time.sleep(0.1)

            click_and_process_more_button(driver, focused_element, message_template, first_name)

        # Check if the focused element is the Follow button
        elif button_text == "message":
            logger.info("Message button found")

            click_and_process_more_button(driver, focused_element, message_template, first_name)

        # Check if the focused element is the Pending button
        elif button_text == "pending":
            logger.info("Connection is Pending, not doing anything")
        
        time.sleep(2)
   
    except Exception as e:
        logger.error(f"Error processing profile {profile_url}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="LinkedIn Profile Visitor and Connection Sender")
    parser.add_argument("--username", required=True, help="LinkedIn username or email")
    parser.add_argument("--password", required=True, help="LinkedIn password")
    parser.add_argument("--messagefile", required=True, help="Path to the file containing the message template")
    parser.add_argument("--pages", type=int, default=1, help="Number of search result pages to process")
    parser.add_argument("--searchurlfile", required=True, help="Path to the file containing the search results URL")
    args = parser.parse_args()

    logger.info("Script started with provided arguments")

    driver = setup_driver()
    logger.info("WebDriver initialized")

    try:
        login_to_linkedin(driver, args.username, args.password)

        logger.info("reading message file")

        with open(args.messagefile, 'r') as file:
            message_template = '\n'.join(line.strip() for line in file if line.strip() and not line.startswith('#'))

        if not message_template:
            print("No valid message template found in the file.")
            exit(1)

        logger.info(f"messagefile read \n {message_template}")

        with open(args.searchurlfile, 'r') as file:
            search_url = next((line.strip() for line in file if line.strip() and not line.startswith('#')), None)

        if search_url is None:
            print("No valid search URL found in the file.")
            exit(1)

        logger.info(f"searchurlfile read \n {search_url}")

        profile_urls = get_profile_links(driver, search_url, args.pages)
        logger.info(f"Found {len(profile_urls)} profile URLs")

        for profile_url in profile_urls:
            visit_profile(driver, profile_url, message_template)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

    finally:
        logger.info("Closing the browser")
        driver.quit()

if __name__ == "__main__":
     main()
