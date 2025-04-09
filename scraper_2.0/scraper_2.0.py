def scraper_parameter_prompt(case):
    while True:
        try:
            item = int(input(f"{case}\n"))
            if item > 0:
                return item
            else:
                print("Invalid input try again!!!")
                continue
        except ValueError:
            print("Invalid input try again!!!")
            continue

def write_links(results):
    count = 0
    file = open('links.txt', 'w')
    for item in results:
        for elements in item:
            count+=1
            file.write(elements + "\n")
    file.close()
    return count
    #print(f"Collected {count} links")

def stage_1(num_pages,num_selenium,num_batches):
    start_time = time.time()
    urls = [
        (f"https://www.myhome.ge/s/iyideba-bina-Tbilisshi/?deal_types=1&re"
         f"al_estate_types=1&cities=1&currency_id=1&CardView=1&page={i}")
        for i in range(1, num_pages + 1)]

    batches = list(split(urls,num_batches))

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_selenium) as executor:
        results = list(executor.map(lg.scrape, batches,range(len(batches))))

    count = write_links(results)
    end_time = time.time()
    execution_time = end_time - start_time
    formatted_time = str(timedelta(seconds=execution_time))
    print(f"Successfully scraped {count} links in {formatted_time}")
    return formatted_time

def write_json(results):
    combined_data = []

    count = 0
    for item in results:
        for elements in item:
            count += 1
            combined_data.append(elements)
    #print(f"Successfully scraped {count} links")
    combined_json = json.dumps(combined_data, indent=4)
    with open(f'raw.json', 'w') as f:
        f.write(combined_json)
    return count
def stage_2(num_workers,batch_per_worker):
    start_time = time.time()
    urls = ls.read_lines("links.txt")
    batches = list(split(urls, num_workers * batch_per_worker))
    results = ls.parallel_data_collector(batches, num_workers)
    count = write_json(results)

    end_time = time.time()
    execution_time = end_time - start_time
    formatted_time = str(timedelta(seconds=execution_time))
    print(f"Successfully scraped {count} links in {formatted_time}")
    return formatted_time

def stage_3():
    start_time = time.time()
    map_grab()
    data = de.data_load("raw.json")
    mapping = de.data_load("mapping.json")
    dataset = []
    for item in data:
        row = de.row_creator(item,mapping)
        dataset.append(row)

    dataset_dumps = json.dumps(dataset, indent = 4)
    with open(f"{date.today()}.json", "w") as f:
        f.write(dataset_dumps)
    end_time = time.time()
    execution_time = end_time - start_time
    formatted_time = str(timedelta(seconds=execution_time))
    return formatted_time


def main():
    num_pages = scraper_parameter_prompt("How many pages do you want to scrape?\n(I do 4050)")
    num_selenium = scraper_parameter_prompt("How many selenium sessions do you want to run?\n(I use 2)")
    num_batches = num_selenium * scraper_parameter_prompt("How many batches do you want per selenium session?\n(I use 4)")
    num_workers = scraper_parameter_prompt("How many workers do you want for the link scraping phase?\n(I use 6)")
    batch_per_worker = scraper_parameter_prompt("How many batches do you want per worker?\n(Sometimes at the end only one batch is left and only one worker is scraping, I recommend >1)\n(I use 5)")

    time_1 = stage_1(num_pages,num_selenium,num_batches)

    time_2 = stage_2(num_workers,batch_per_worker)

    time_3 = stage_3()
    print(f"Phase one took {time_1}, phase two took {time_2}, and phase three took {time_3}")


import link_gather as lg
from split import split
import concurrent.futures
import link_scrape as ls
import json
import time
from datetime import timedelta
from datetime import date
import data_extract as de
from mapping_grab import map_grab

main()