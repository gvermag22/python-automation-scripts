import sys
import time
import logging
import argparse
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

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

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=option)
    return driver

def facebook_login(driver, email, password):
    """Log in to Facebook."""
    logger.info("Attempting to log in to Facebook")
    driver.get('https://www.facebook.com/')
    time.sleep(5)  # Delay before interacting with the login page

    try:
        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
        password_input = driver.find_element(By.ID, 'pass')
        login_button = driver.find_element(By.NAME, 'login')

        email_input.send_keys(email)
        password_input.send_keys(password)
        login_button.click()

        # Use a verified CSS selector or XPath
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), \"What's on your mind\")]"))
        )

        logger.info("Login successful")

    except (TimeoutException, NoSuchElementException) as e:
        logger.error(f"Login failed: {str(e)}")
        raise

def switch_profile(driver, profile_url):
    """Switch to the preferred Facebook profile."""
    logger.info(f"Attempting to switch to profile: {profile_url}")
    driver.get(profile_url)
    time.sleep(5)  # Delay before trying to switch profiles

    try:
        switch_profile_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Switch Now']"))
        )
        switch_profile_button.click()
        logger.info("Clicked 'Switch Profile' button")
        
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Account']")))
        
        logger.info("Profile switch completed")
    except TimeoutException:
        logger.warning("'Switch Profile' button not found or not clickable")

def post_in_group(driver, group_url, message):
    """Post a message in a Facebook group."""
    logger.info(f"Attempting to post in group: {group_url}")
    driver.get(group_url)
    time.sleep(5)  # Initial delay to ensure the page loads

    try:
        # Wait for the post box to be clickable and click it
        post_box = WebDriverWait(driver, 25).until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Write something...']"))
        )
        post_box.click()

        time.sleep(5)

        # Type the message character by character to avoid triggering shortcuts
        for char in message:
            actions = ActionChains(driver)
            actions.send_keys(char)
            time.sleep(0.02)
            actions.perform()

        time.sleep(5)
        post_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Post']"))
        )
        post_button.click()

        time.sleep(5)

        logger.info("Post successful")

    except (TimeoutException, NoSuchElementException) as e:
        logger.error(f"Failed to post in group: {str(e)}")
        raise

def read_file(file_path):
    """Read content from a file."""
    with open(file_path, 'r') as f:
        content = f.read().strip()
    return content

def read_group_urls(groups_file):
    """Read group URLs from file, ignoring commented lines."""
    with open(groups_file, 'r') as f:
        group_urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    logger.info(f"Found {len(group_urls)} active group URLs")
    return group_urls

def main(username, password, message_file, groups_file, profile_url_file, headless):
    """Main function to execute the Facebook posting script."""
    if not os.path.isfile(message_file):
        logger.error(f"Message file '{message_file}' does not exist.")
        return
    if not os.path.isfile(groups_file):
        logger.error(f"Groups file '{groups_file}' does not exist.")
        return
    if not os.path.isfile(profile_url_file):
        logger.error(f"Profile URL file '{profile_url_file}' does not exist.")
        return

    driver = setup_driver(headless)

    try:
        facebook_login(driver, username, password)
        time.sleep(5)  # Delay before switching profile

        profile_url = read_file(profile_url_file)
        logger.info(f"Read profile URL: {profile_url}")

        switch_profile(driver, profile_url)
        time.sleep(5)  # Delay before reading message

        message = read_file(message_file)
        group_urls = read_group_urls(groups_file)

        for group_url in group_urls:
            try:
                post_in_group(driver, group_url, message)
                time.sleep(10)  # Delay between posting in different groups
            except Exception as e:
                logger.error(f"Error posting in group {group_url}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Group Poster")
    parser.add_argument("--username", required=True, help="Facebook username/email")
    parser.add_argument("--password", required=True, help="Facebook password")
    parser.add_argument("--message_file", required=True, help="Path to file containing the message to post")
    parser.add_argument("--groups_file", required=True, help="Path to file containing group URLs")
    parser.add_argument("--profile_url_file", required=True, help="Path to file containing the profile URL")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")

    args = parser.parse_args()

    main(args.username, args.password, args.message_file, args.groups_file, args.profile_url_file, args.headless)
