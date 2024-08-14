from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from amazoncaptcha import AmazonCaptcha
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def change_zip_code(code, driver):
    time.sleep(3)
    driver.find_element(By.XPATH, "//*[@id='nav-main']/div[1]/div/div/div[3]/span[1]/span/input").click()
    driver.find_element(By.XPATH,"//*[@id='nav-global-location-popover-link']").click()
    wait = WebDriverWait(driver, 5)
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='GLUXZipUpdateInput']"))).send_keys(code)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='GLUXZipUpdate']/span/input"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='nav-global-location-popover-link']")))
    driver.refresh()
    time.sleep(2)
def solve_captcha(driver):
    """
    Attempts to solve a CAPTCHA on the page using the AmazonCaptcha library.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.

    Returns:
        bool: True if CAPTCHA was solved and submitted, False otherwise.
    """
    try:
        # Attempt to find the CAPTCHA image element
        image_element = driver.find_element(By.XPATH, "/html/body/div/div[1]/div[3]/div/div/form/div[1]/div/div/div[1]/img")
        image_src = image_element.get_attribute("src")
        print("Image source:", image_src)

        # If the image is found, solve the CAPTCHA
        if image_src:
            captcha = AmazonCaptcha.fromlink(image_src)
            captcha_solution = captcha.solve()
            print("CAPTCHA Solution:", captcha_solution)
            driver.find_element(By.ID, "captchacharacters").send_keys(captcha_solution)
            driver.find_element(By.XPATH, "/html/body/div/div[1]/div[3]/div/div/form/div[2]/div/span/span/button").click()
            return True
        else:
            print("No CAPTCHA image source found.")
            return False

    except NoSuchElementException:
        print("CAPTCHA not found, continuing with the rest of the code.")
        return False
def search(to_search,driver):
    driver.find_element(By.XPATH, "//*[@id='twotabsearchtextbox']").send_keys(to_search)
    driver.find_element(By.XPATH, "//*[@id='nav-search-submit-button']").click()
def get_product_data(driver, link):
    driver.get(link)
    product_info = {
        "Title": "",
        "Price": "",
        "Reviews": []
    }
    
    time.sleep(3)
    
    try:
        title = driver.find_element(By.XPATH, "//*[@id='title']").text
        product_info["Title"] = title
    except NoSuchElementException:
        print("Title element not found.")
        product_info["Title"] = "Title not found"

    try:
        price = driver.find_element(By.XPATH, "//*[@id='corePrice_feature_div']/div/div/div/div/span[1]/span[2]/span[2]").text
        product_info["Price"] = price
    except NoSuchElementException:
        print("Price element not found.")
        product_info["Price"] = "Price not found"
    
    print("Waiting to find reviews")
    time.sleep(3)
    
    reviews = find_reviews(driver)
    product_info["Reviews"] = reviews
    
    return product_info
def find_reviews(driver):
    reviews = []

    try:
        # Click on the "See all reviews" button
        driver.find_element(By.XPATH, "//*[@id='cr-pagination-footer-0']/a").click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@data-hook="review-body"]//span'))
        )
        i=0
        while True:
            # Collect all review bodies on the current page
            time.sleep(5)
            review_bodies = driver.find_elements(By.XPATH, '//*[@data-hook="review-body"]//span')
            
            for review_body in review_bodies:
                print(i)
                reviews.append(review_body.text)
                i+=1
            # Check if the "Next page" button is disabled
            
            next_page_element = driver.find_element(By.XPATH, "//*[@id='cm_cr-pagination_bar']/ul/li[2]/a")
            if "a-disabled" in next_page_element.get_attribute("class"):
                print("Reached the last page.")
                break
            print("here finding next page button")
            # Wait until the next page button is clickable
            time.sleep(3)
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='cm_cr-pagination_bar']/ul/li[2]/a"))
            )
            next_button.click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@data-hook="review-body"]//span'))
            )
    except (NoSuchElementException, TimeoutException):
        print("An error occurred while trying to find or click the next page button.")
    return reviews
def search_links(driver):
    links = []
    wait = WebDriverWait(driver, 10)
    i=0
    while True:
        try: 
            elements = driver.find_elements(By.XPATH, '//h2/a[@href]')
            for element in elements:
                link = element.get_attribute("href")
                links.append(link)
            print(i),
            i+=1
            time.sleep(3)
            
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "s-pagination-next")]')))
            if 's-pagination-disabled' in next_button.get_attribute('class'):
                print("Reached the last page.")
                return links
            next_button.click()
        except Exception as e:
            print(f"An error occurred: {e}")
            print("here i am goig men bas aur links nahi hai")
            return links
            break
        
    return links


def append_to_csv(product_info, filename='product_reviews.csv'):
    # Convert product information to a list of rows
    rows = []
    title = product_info.get("Title", "Title not found")
    price = product_info.get("Price", "Price not found")
    
    for review in product_info.get("Reviews", []):
        rows.append({"Title": title, "Price": price, "Review": review})

    df = pd.DataFrame(rows)

    # Append DataFrame to CSV file
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, mode='w', header=True, index=False)
    
    print(f"Data appended to {filename} successfully.")