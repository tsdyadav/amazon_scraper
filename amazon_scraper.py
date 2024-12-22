import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import os

# Replace these with your Amazon credentials
USERNAME = "your_amazon_email@example.com"
PASSWORD = "your_amazon_password"

# Categories to scrape (update as needed)
CATEGORIES_URLS = [
    "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
    "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
    "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
    "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0",
    "https://www.amazon.in/gp/bestsellers/home/ref=zg_bs_nav_home_0",
    "https://www.amazon.in/gp/bestsellers/books/ref=zg_bs_nav_books_0",
    "https://www.amazon.in/gp/bestsellers/toys/ref=zg_bs_nav_toys_0",
    "https://www.amazon.in/gp/bestsellers/fashion/ref=zg_bs_nav_fashion_0",
    "https://www.amazon.in/gp/bestsellers/beauty/ref=zg_bs_nav_beauty_0",
    "https://www.amazon.in/gp/bestsellers/grocery/ref=zg_bs_nav_grocery_0"
]

# Function to set up the Selenium WebDriver
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    driver_service = Service("path_to_chromedriver")
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)
    return driver

# Function to log in to Amazon
def amazon_login(driver):
    driver.get("https://www.amazon.in/ap/signin")
    try:
        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email")))
        email_input.send_keys(USERNAME)
        email_input.send_keys(Keys.RETURN)
        
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password")))
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)
        
        print("Login successful!")
        time.sleep(3)
    except TimeoutException:
        print("Login failed. Check credentials or page structure.")
        driver.quit()
        exit()

# Function to scrape products in a category
def scrape_category(driver, category_url, category_name):
    print(f"Scraping category: {category_name}")
    driver.get(category_url)
    scraped_data = []

    products_scraped = 0
    MAX_PRODUCTS = 1500

    while products_scraped < MAX_PRODUCTS:
        time.sleep(3)
        products = driver.find_elements(By.CSS_SELECTOR, "div.zg-grid-general-faceout")
        for product in products:
            if products_scraped >= MAX_PRODUCTS:
                break
            try:
                name = product.find_element(By.CSS_SELECTOR, "div.p13n-sc-truncated").text
                price = product.find_element(By.CSS_SELECTOR, "span.p13n-sc-price").text
                discount = product.find_element(By.CSS_SELECTOR, "span.a-color-price").text
                rating = product.find_element(By.CSS_SELECTOR, "span.a-icon-alt").text
                
                if "50%" in discount:
                    product_details = {
                        "Category": category_name,
                        "Product Name": name,
                        "Price": price,
                        "Discount": discount,
                        "Rating": rating,
                        "Ship From": "Not Available",
                        "Sold By": "Not Available",
                        "Product Description": "Not Available",
                        "Number Bought in the Past Month": "Not Available",
                        "Images": []
                    }
                    
                    try:
                        product_details["Ship From"] = product.find_element(By.CSS_SELECTOR, "span.ship-from").text
                    except NoSuchElementException:
                        pass
                    try:
                        product_details["Sold By"] = product.find_element(By.CSS_SELECTOR, "span.sold-by").text
                    except NoSuchElementException:
                        pass
                    try:
                        product_details["Product Description"] = product.find_element(By.CSS_SELECTOR, "div.product-description").text
                    except NoSuchElementException:
                        pass
                    try:
                        product_details["Number Bought in the Past Month"] = product.find_element(By.CSS_SELECTOR, "span.number-bought").text
                    except NoSuchElementException:
                        pass
                    try:
                        images = product.find_elements(By.CSS_SELECTOR, "img")
                        product_details["Images"] = [img.get_attribute("src") for img in images]
                    except NoSuchElementException:
                        pass

                    scraped_data.append(product_details)
                    products_scraped += 1
            except NoSuchElementException:
                continue

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.a-last a")
            driver.execute_script("arguments[0].click();", next_button)
        except NoSuchElementException:
            print("  No more pages.")
            break

    return scraped_data

# Main function
def main():
    driver = setup_driver()
    try:
        amazon_login(driver)
        all_data = []

        for category_url in CATEGORIES_URLS:
            category_name = category_url.split("/")[5].capitalize()
            data = scrape_category(driver, category_url, category_name)
            all_data.extend(data)
    finally:
        driver.quit()

    with open("amazon_best_sellers.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print("Data saved to amazon_best_sellers.json")

if __name__ == "__main__":
    main()
