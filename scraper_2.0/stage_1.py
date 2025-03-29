from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import concurrent.futures
import tempfile
from selenium.common.exceptions import StaleElementReferenceException

# Number of pages to scrape
k = 4050

urls = [f"https://www.myhome.ge/s/iyideba-bina-Tbilisshi/?deal_types=1&real_estate_types=1&cities=1&currency_id=1&CardView=1&page={i}" for i in range(1, k+1)]

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

batches = list(split(urls,2))

def scrape(batch):
    batch_id = batch[0][-5:]
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Simpler headless mode
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Prevent memory issues
    options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")  # Unique temp profile
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_extension("UBlock.crx")
    driver = webdriver.Remote(command_executor="http://localhost:4444", options=options)
    driver.set_window_size(1280, 720)

    hrefs = []
    driver.implicitly_wait(15)
    i = 0
    #file_write = open(f'temp{batch_id}.txt', 'w')
    for url in batch:
        i+= 1
        print(f"Processing {i}/{len(batch)} for batch {batch_id} \n")
        driver.get(url)
        try:
            #print("Element search")
            my_elements = driver.find_elements(By.CSS_SELECTOR,".group.relative.block.overflow-hidden.rounded-xl.transition-all.duration-500.shadow-devCard.w-full.pt-2.cursor-default.lg\\:cursor-pointer")
            for element in my_elements:
                #print("link search")
                try:
                    href_value = element.get_attribute("href")
                    hrefs.append(href_value)
                    #file_write.write(href_value + "\n")
                except StaleElementReferenceException:
                    print("Failure")
        except NoSuchElementException:
            print(f"No href found for {url}")
        print(f"For batch {batch_id} we have collected {len(hrefs)} links")
    #file_write.close()
    driver.quit()
    return hrefs

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(scrape, batches))

sum = 0
for res in results:
    print(res)
    print(len(res))
    sum += len(res)
print(sum)

file = open('itemsV2.txt','w')
for item in results:
    for elements in item:
        file.write(elements+"\n")
file.close()

# java -jar selenium-server-4.30.0.jar standalone
# http://localhost:4444/ui/