from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import tempfile
from selenium.common.exceptions import StaleElementReferenceException

def scrape(batch,batch_id):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Simpler headless mode
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Prevent memory issues
    options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")  # Unique temp profile
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Remote(command_executor="http://localhost:4444", options=options)
    driver.set_window_size(1280, 720)

    hrefs = []
    driver.implicitly_wait(15) # If the element we are waiting for does not load, it will wait for 15 seconds. If it loads it won't wait anymore.
    i = 0
    for url in batch:
        i+= 1
        print(f"Processing {i}/{len(batch)} for batch {batch_id} \n")
        driver.get(url)
        try:
            # Here it grabs the elements that we want. This also tells the scraper to wait for these elements
            my_elements = driver.find_elements(By.CSS_SELECTOR,".group.relative.block.overflow-hidden.rounded-xl.transition-all.duration-500.shadow-devCard.w-full.pt-2.cursor-default.lg\\:cursor-pointer")
            for element in my_elements:
                try:
                    # Here we save the links, sometimes the one of the links may fail
                    href_value = element.get_attribute("href")
                    hrefs.append(href_value)
                except StaleElementReferenceException:
                    print("Failure")
        except NoSuchElementException:
            print(f"No href found for {url}")
        print(f"For batch {batch_id} we have collected {len(hrefs)} links")
    driver.quit()
    return hrefs
