from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # Import the Keys class
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import argparse
import logging
import re
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_driver(headless=False):
    """Set up the Chrome WebDriver with options."""
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")
    option.add_experimental_option("prefs", { 
        "profile.default_content_setting_values.notifications": 2 
    })
    if headless:
        option.add_argument("--headless")

    # Get the path to the ChromeDriver executable
    driver_path = ChromeDriverManager().install()

    # Create a Service object with the driver path
    from selenium.webdriver.chrome.service import Service
    service = Service(driver_path)

    # Initialize the WebDriver with the service object
    driver = webdriver.Chrome(service=service, options=option)
    return driver

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def login_to_linkedin(driver, username, password):
    """Log in to LinkedIn."""
    logger.info("Navigating to LinkedIn login page")
    driver.get("https://www.linkedin.com/login")
    driver.maximize_window()

    try:
        # Enter login credentials
        logger.info("Entering login credentials")
        username_field = driver.find_element(By.XPATH, "//*[@id='username']")
        username_field.send_keys(username)
        username_field.send_keys(Keys.TAB)  # Tab into the password field
        time.sleep(1)  # Wait for the password field to be focused
        actions = webdriver.ActionChains(driver)
        actions.send_keys(password).perform()  # Enter the password
        login_button = driver.find_element(By.XPATH, "//button[@aria-label='Sign in']")
        login_button.click()
        logger.info("Login credentials entered and login button clicked")

    except NoSuchElementException as e:
        logger.error(f"Failed to find an element: {str(e)}")
        raise

    # Wait for login to complete
    time.sleep(5)
    logger.info("Waited for login to complete")


def send_message(driver, profile_url, name, message, attachment_path=None):
    """Send a message to a LinkedIn profile."""
    logger.info(f"Navigating to profile: {profile_url}")
    if not profile_url.startswith("http"):
        profile_url = "https://" + profile_url
    driver.get(profile_url)

    time.sleep(5)

    try:
        # Find the element with the ID top-card-text-details-contact-info
        element = driver.find_element(By.XPATH, '//*[@id="top-card-text-details-contact-info"]')
        element.click()  # Click on the element to focus it

        # Press escape to close any popup that may have opened
        actions = ActionChains(driver)
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(0.1)

        # Press tab twice to focus on the message button
        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.1)
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.1)

        # Press enter to bring up the popup
        actions.send_keys(Keys.RETURN).perform()

        time.sleep(5)

        # Type in the name character by character
        logger.info("Typing in the name")
        for char in name:
            actions = ActionChains(driver)
            actions.send_keys(char)
            time.sleep(0.02)
            actions.perform()

        # Type in two new lines
        actions = ActionChains(driver)
        actions.send_keys(Keys.RETURN).perform()
        time.sleep(0.1)
        actions.send_keys(Keys.RETURN).perform()
        time.sleep(0.1)

        # Type in the message character by character
        logger.info("Typing in the message")
        for char in message:
            actions = ActionChains(driver)
            actions.send_keys(char)
            time.sleep(0.02)
            actions.perform()

        if attachment_path:
            # Click on the attachment button
            attachment_button = driver.find_element(By.XPATH, '//*[@id="attachment-trigger-ember1492"]')
            attachment_button.click()
            time.sleep(1)

            # Find the input element with type file
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(attachment_path)
            time.sleep(2)

            # Tab to the send button
            logger.info("Tabbing to the send button")
            for _ in range(3):
                actions = ActionChains(driver)
                actions.send_keys(Keys.TAB).perform()
                time.sleep(0.1)
        else:
            # Tab to the send button
            logger.info("Tabbing to the send button")
            for _ in range(6):
                actions = ActionChains(driver)
                actions.send_keys(Keys.TAB).perform()
                time.sleep(0.1)

        # Press enter to send the message
        logger.info("Pressing enter to send the message")
        actions = ActionChains(driver)
        actions.send_keys(Keys.RETURN).perform()

        time.sleep(5)

        logger.info("Message sent successfully")

    except Exception as e:
        logger.error(f"Failed to send message to {profile_url}: {str(e)}")
        with open("notsent.log", "a") as file:
            file.write(f"{datetime.now()} - {profile_url}\n")

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Message Sender")
    parser.add_argument("--username", required=True, help="LinkedIn username or email")
    parser.add_argument("--password", required=True, help="LinkedIn password")
    parser.add_argument("--inputfile", required=True, help="Path to the input file containing profile URLs")
    parser.add_argument("--messagefile", required=True, help="Path to the input file containing the message")
    parser.add_argument("--attachmentfile", help="Path to the attachment file")
    args = parser.parse_args()

    logger.info("Script started with provided arguments")

    # Initialize the WebDriver
    driver = setup_driver(False)
    logger.info("WebDriver initialized")

    try:
        # Log in to LinkedIn
        login_to_linkedin(driver, args.username, args.password)

        # Read profiles from the input file
        with open(args.inputfile, 'r') as file:
            profiles = file.readlines()
            profiles = [profile.strip() for profile in profiles if not profile.strip().startswith('#')]
            profiles = [profile.split(',') for profile in profiles]

        # Read the message from the input file
        with open(args.messagefile, 'r') as file:
            message_lines = file.readlines()
            message_lines = [line.strip() for line in message_lines if not line.strip().startswith('#')]
            message = '\n'.join(message_lines)

        # Send messages to each profile
        for profile in profiles:
            name = profile[0].strip()
            linkedin_url = profile[1].strip()
            if args.attachmentfile:
                send_message(driver, linkedin_url, name, message, args.attachmentfile)
            else:
                send_message(driver, linkedin_url, name, message)
            time.sleep(2)  # Delay between sending messages

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        # Close the browser
        logger.info("Closing the browser")
        driver.quit()

if __name__ == "__main__":
    main()
