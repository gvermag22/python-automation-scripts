from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import argparse
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def login_and_collect_links(username, password, profile_url):
    logger.info("Starting the Facebook Group Link Collector")
    
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-notifications")
    logger.info("Chrome options set up")

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    logger.info("WebDriver initialized")

    try:
        # Log in to Facebook
        logger.info("Navigating to Facebook login page")
        driver.get("https://www.facebook.com")
        driver.maximize_window()

        # Accept cookies if prompted
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))).click()
            logger.info("Accepted cookies")
        except TimeoutException:
            logger.info("No cookie acceptance needed or button not found")

        # Enter login credentials
        logger.info("Entering login credentials")
        email = driver.find_element(By.ID, "email")
        email.send_keys(username)
        password_field = driver.find_element(By.ID, "pass")
        password_field.send_keys(password)
        login_button = driver.find_element(By.NAME, "login")
        login_button.click()
        logger.info("Login credentials entered and login button clicked")

        # Wait for login to complete
        time.sleep(5)
        logger.info("Waited for login to complete")

        # Switch profile if specified
        if profile_url:
            switch_profile(driver, profile_url)

        # Navigate to the specified URL
        logger.info("Navigating to Facebook groups page")
        driver.get("https://www.facebook.com/groups/joins/?nav_source=tab")
        time.sleep(5)

        group_links = set()  # Using a set to avoid duplicates

        # Function to scroll and collect links
        def scroll_and_collect_links():
            logger.info("Starting to scroll and collect links")
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # Find all group links
                links = driver.find_elements(By.XPATH, "//a[contains(@href, '/groups/')]")
                logger.info(f"Found {len(links)} potential group links")
                
                for link in links:
                    href = link.get_attribute('href')
                    # Filter out non-group links
                    if href and '/groups/' in href and not any(x in href for x in ['discover', 'feed', 'joins']):
                        # Remove trailing content starting from ?notif_id= or ?ref=
                        clean_href = re.sub(r'[?](?:notif_id|ref)=.*', '', href)
                        if clean_href not in group_links:
                            group_links.add(clean_href)
                            logger.info(f"Added new group link: {clean_href}")

                # Check if we've reached the bottom of the page
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    logger.info("Reached the bottom of the page")
                    break
                last_height = new_height

        # Scroll and collect links
        scroll_and_collect_links()

        # Save links to file
        logger.info("Saving collected links to file")
        with open("facebook_groups.txt", "w") as f:
            for link in group_links:
                f.write(link + "\n")

        logger.info(f"Saved {len(group_links)} group links to facebook_groups.txt")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        # Close the browser
        logger.info("Closing the browser")
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Group Link Collector")
    parser.add_argument("--username", required=True, help="Facebook username or email")
    parser.add_argument("--password", required=True, help="Facebook password")
    parser.add_argument("--profileurl", help="URL of the profile to switch to (optional)", default=None)
    args = parser.parse_args()

    logger.info("Script started with provided arguments")
    login_and_collect_links(args.username, args.password, args.profileurl)
    logger.info("Script execution completed")
